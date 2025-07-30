""" Download songs or playlists from Suno to a local folder

Usage: sunodl [options] [<url>...]

General options:
    -o, --output DIR     Output path [default: .]
    -f, --force          Overwrite destination files
    -u, --upsampled      Follow upsample links (experimental)
    --no-id3             Do not add ID3 tags

Output control:
    -v, --verbose        Verbose output
    -D, --debug          Even more verbose output
    -p, --progress MODE  Progress bar on/off [default: auto]

Debugging options:
    -N, --dryrun         Show what would be downloaded, but don't download
    -J, --json           Dump object metadata as json
    -Y, --yaml           Dump object metadata as yaml
    -P, --pdb            Start debugger on crash
    -V, --version        Print version
    -h, --help           Print this help

Notes:
    The url arguments can be copy-pasted from your web browser. They're the
    ones that appear in the location bar when looking at songs/playlists on
    suno.com.

    I am not sure what the "upsampled" versions of songs actually do. The
    Suno website appears to use them sometimes but not always. I've compared
    a few individual files and they don't seem to differ much in size or
    metadata reported by the `file` utility.
"""

import dataclasses as dc
import io
import json
import logging
import logging.config
import pdb
import re
import sys
import textwrap
from functools import cache, partial
from importlib.resources import files as pkgfiles
from operator import itemgetter
from pathlib import Path
from time import sleep

import mutagen
import requests
import yaml
from addict import Dict
from appdirs import user_config_dir
from docopt import docopt
from mutagen.easyid3 import EasyID3 as ID3
from mutagen.id3 import USLT, APIC
from requests.exceptions import HTTPError
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .version import version

log = logging.getLogger(__name__)
ydump = partial(yaml.dump, Dumper=yaml.SafeDumper)
yload = partial(yaml.load, Loader=yaml.SafeLoader)


class FatalError(Exception):
    """ Fatal errors raised by this module.

    Produces a clean error message unless --debug or --pdb is set, in
    which case they're treated as a crash and produce a trace.
    """


class Toggle:
    """ Helper for options that can be on/off/auto. """
    # At the moment this is only used for --progress
    enabled = {"on": True,
               "off": False,
               "auto": None}

    def __init__(self, name, value):
        self.value = value.lower().strip()
        if self.value not in self.enabled:
            raise FatalError(f"{name} must be one of {set(self.enabled)}, "
                             f"not '{value}'")
        self.enabled = type(self).enabled[self.value]

    def __str__(self):
        return self.value

    @property
    def disabled(self):
        """ Check if the toggle is disabled.

        Not quite as simple as `not obj.enabled`, because of None/auto.
        """
        return (False if self.enabled is True
                else True if self.enabled is False
                else None)


class Args(Dict):
    """ Convenience wrapper for the docopt dict

    This exists so I can do args.whatever and get the Right Thing out of it.
    """

    keyfmts = ['{key}',
               '-{key}',
               '--{key}',
               '<{key}>']

    def _realkey(self, key):
        # Look for the first key-variant that's present, otherwise use the
        # original key. Replace underscores with dashes to support dot
        # lookups of those options.
        key = key.replace('_', '-')
        for fmt in type(self).keyfmts:
            realkey = fmt.format(key=key)
            if realkey in self:
                return realkey
        return key

    def __getitem__(self, key):
        key = self._realkey(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = self._realkey(key)
        super().__setitem__(key, value)

    @property
    def progress(self):
        """ Interpret the --progress option. """
        # We do this on first access so any conversion exceptions happen
        # inside main handler, thus subject to --pdb etc.
        return Toggle('--progress', self['--progress'])


class Playlist(Dict):
    """ Representation of a playlist """
    # NOTE: the playlist_clips field of the returned data appears exactly the
    # same as that from looking up the clip directly, except that looking up
    # the clip also has a "is_following_creator" field (that we don't care
    # about).
    @property
    def songs(self):
        """ Get the songs in this playlist, in order. """
        clips = self.playlist_clips
        sorter = itemgetter('relative_index', None)
        return [clip.clip for clip in sorted(clips, key=sorter)]

    def __str__(self):
        return str(self.name or repr(self))


class Song(Dict):
    """ Representation of a song. """
    @property
    def lyrics(self):
        """ Alias for song lyrics. """
        return self.get('lyrics', self.metadata.prompt, None) or Dict()

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.title


def register_mutagen_keys():
    """ Add EasyID3 keys for lyrics and images. """
    # convenience aliases
    utf8 = mutagen.id3.Encoding.UTF8
    ptype = mutagen.id3.PictureType
    # pylint: disable=unused-argument

    def get_lyrics(id3, key):
        """ Retrieve lyrics. """
        return [uslt.text for uslt in id3.getall('USLT')]

    def set_lyrics(id3, key, value):
        """ Set lyrics. """
        log.debug("settings lyrics of length %s", len(value))
        id3.delall('USLT')
        for v in value:
            id3.add(USLT(encoding=utf8, desc="prompt", text=v))

    def delete_lyrics(id3, key):
        """ Delete lyrics. """
        id3.delall('USLT')

    def get_images(id3, key, _type=None):
        """ Get images. """
        return [apic.data for apic in id3.getall('APIC')
                if _type is None or _type == apic.type]

    def set_images(id3, key, value, _type):
        """ Set images. """
        value = [value] if isinstance(value, bytes) else value
        # Keep images not associated with this type
        images = [apic for apic in id3.getall('APIC')
                  if _type != apic.type]
        for v in value:
            apic = APIC(data=v,
                        encoding=utf8,
                        mime='image/jpeg',  # FIXME: detect this
                        desc=key,
                        type=_type)
            images.append(apic)
        id3.setall('APIC', images)

    def delete_images(id3, key, _type):
        """ Delete images. """
        keep = [apic for apic in id3.getall('APIC')
                if apic.type != _type]
        id3.setall('APIC', keep)

    def mk_imgfuncs(_type):
        return {"getter": partial(get_images, _type=_type),
                "setter": partial(set_images, _type=_type),
                "deleter": partial(delete_images, _type=_type)}

    ID3.RegisterKey('lyrics', get_lyrics, set_lyrics, delete_lyrics)
    ID3.RegisterKey('cover', **mk_imgfuncs(ptype.COVER_FRONT))
    ID3.RegisterKey('illustration', **mk_imgfuncs(ptype.ILLUSTRATION))
    log.debug("mutagen keys registered")


class Session(requests.Session):
    """ Customized session with helper functions. """

    @staticmethod
    def fail_on_http_error(response, *_, **__):
        """ Response hook for error handling. """
        # TODO: Try to identify breakage due to upstream API changes.
        try:
            response.raise_for_status()
        except HTTPError as ex:
            raise FatalError(ex) from ex

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hooks['response'].append(self.fail_on_http_error)

    def download(self, url, **kwargs):
        """ Download a file. """
        data = io.BytesIO()
        resp = self.get(url, stream=True, **kwargs)
        size = int(resp.headers.get('content-length', 0))
        log.debug("downloading %s (purported size %s)", url, size)
        for chunk in resp.iter_content(None):
            log.debug("received chunk of length %s", len(chunk))
            data.write(chunk)
        return data.getvalue()


@dc.dataclass
class Suno:
    """ Interface to Suno APIs. """
    endpoints: Dict
    session: Session = dc.field(default_factory=Session)
    types = {'playlist': Playlist, 'song': Dict}
    regex = re.compile(
        r'https://[^/]+/'
        r'(?P<type>[^/]+)/'
        r'(?P<id>[^-]{8}-[^-]{4}-[^-]{4}-[^-]{4}-[^-]{12})'
        r'(?:/|$)'
    )

    def get(self, url):
        """ Get a suno object given a copy-pasted URL from the browser. """
        match = self.regex.match(url)
        if not match:
            raise FatalError(f"url pattern malformed or unknown: {url}")
        otype, oid = match.groups()
        if otype not in self.types:
            raise FatalError(f"unknown object type '{otype}' in url {url}")
        data_url = self.endpoints[otype].format(id=oid)
        return self.types[otype](self.session.get(data_url).json())

    def clip(self, clip_id):
        """ Get a clip (song) by id."""
        url = self.endpoints.clip.format(id=clip_id)
        return Song(self.session.get(url).json())

    def playlist(self, playlist_id):
        """ Get a Playlist object by ID """
        url = self.endpoints.playlist.format(id=playlist_id)
        return Playlist(self.session.get(url).json())

    def upsampled(self, clip):
        """ Get the upsampled version of a clip. """
        while ucid := clip.metadata.upsample_clip_id:
            log.debug("following upsample id %s -> %s", clip.id, ucid)
            clip = self.clip(ucid)
        return clip

    def id3tags(self, song, playlist=None, track=None):
        """ Generate ID3 tags for an mp3. """
        download = self.session.download  # convenience alias
        playlist = playlist or Dict()     # so lookups below fail gracefully
        track = track or playlist and playlist.songs.index(song)
        return {
            "album": playlist and playlist.name,
            "albumartist": playlist and playlist.user_display_name,
            "title": song.title,
            "artist": song.display_name,
            "tracknumber": str(track),
            "date": song.created_at,
            "lyrics": song.lyrics,
            "illustration": song.image_url and download(song.image_url),
            "cover": playlist.image_url and download(playlist.image_url),
        }


@cache
def initconf():
    """ Load yaml config files.

    Packaged yaml files are loaded first, then those in the user config
    directory, each in lexicographic order. Last setting wins. The returned
    dataset is cached; repeat calls will return the cached data. To force a
    reload, call initcfg.cache_clear.
    """
    dataset = Dict()
    paths = {'default': pkgfiles(__name__),
             'user': Path(user_config_dir('sunodl'))}
    for src, path in paths.items():
        # log one line per file, but make sure the directrories involved are
        # identified even if missing or empty, to aid debugging.
        if not path.is_dir():
            log.debug("skipping %s config dir: %s (no such dir)", src, path)
            continue
        files = sorted(f for f in path.iterdir() if f.suffix == '.yaml')
        if not files:
            log.debug("skipping %s config dir: %s (no yaml files)", src, path)
            continue
        for file in files:
            log.debug("loading %s config file: %s", src, file)
            dataset.update(Dict(yload(file.read_text())))
    log.debug("%s", ydump({'effective config': dataset.to_dict()}).strip())
    return dataset


def initlog(args, conf=None):
    """ Set up logging """
    lvl = ('debug' if args.debug
           else 'info' if args.verbose or args.dryrun
           else 'error' if args.quiet
           else conf.logging.root.level if conf
           else 'warning')
    if conf is None:
        # Config hasn't been loaded yet, just get the basics
        logging.basicConfig(level=lvl.upper(), format="%(message)s")
        log.debug("basic logging initialized")
    else:
        conf.logging.root.level = lvl.upper()
        logging.config.dictConfig(conf.logging)
        log.debug("full logging initialized")


def run(args, conf):
    """ Main program logic """
    suno = Suno(conf.endpoints)
    for url in args.url:
        obj = suno.get(url)
        if args.json:
            print(json.dumps(obj.to_dict()))
            continue
        if args.yaml:
            print(ydump(obj.to_dict()))
            continue
        playlist = obj if isinstance(obj, Playlist) else None
        songs = playlist.songs if playlist else [obj]
        log.info('downloading %s "%s" (%s song(s))',
                 obj.entity_type, obj.name or obj.title, len(songs))
        pbar = tqdm(songs,
                    bar_format="[{n:>2}/{total:<2}]  [{bar:20}]  {desc}",
                    disable=len(songs) <= 1 or args.progress.disabled)
        for i, song in enumerate(pbar, 1):
            if args.upsampled:
                song = suno.upsampled(song)
            # For playlists, prefix mp3 filenames with a number.
            prefix = f"{i:0{len(str(pbar.total))}}_" if playlist else ""
            outfile = Path(args.output,
                           playlist.name if playlist else "",
                           f"{prefix}{song.title}.mp3")
            pbar.set_description_str(song.title)
            log.info("%s -> %s", song.audio_url, outfile)
            if args.dryrun:
                sleep(conf.debug.sleep)  # so we can test bar movement
                continue
            outfile.parent.mkdir(exist_ok=True)
            mp3 = io.BytesIO(suno.session.download(song.audio_url))
            if not args.no_id3:
                tags = ID3(mp3)
                tags.update(suno.id3tags(song, playlist, i))
                tags.save(mp3)
            with outfile.open("wb" if args.force else "xb") as f:
                f.write(mp3.getvalue())


def main(argv=None):
    """ Entry point for sunodl."""
    args = Args(docopt(__doc__.strip(), argv, version=version))
    initlog(args, None)  # So we get debug messages from initconf
    conf = initconf()
    initlog(args, conf)
    register_mutagen_keys()

    # "Expected" exception types exit with an error message, unless debugging
    # information is specifically requested, in which case they're treated as
    # a crash (so you get e.g. a stack trace).
    expected = (() if args.debug
                else (FatalError, FileExistsError,
                      FileNotFoundError, NotImplementedError))

    try:
        with logging_redirect_tqdm():
            run(args, conf)
    except KeyboardInterrupt:
        log.error("keyboard interrupt; aborting")
        sys.exit(2)
    except expected as ex:
        log.error(ex)
        sys.exit(2)
    except Exception as ex:  # pylint: disable=broad-except
        # I want to break this into a function and use it as excepthook, but
        # every time I try it doesn't work.
        log.exception(ex)
        if not args.pdb:
            sys.exit(2)
        print("\n\nCRASH -- UNHANDLED EXCEPTION")
        msg = ("Starting debugger post-mortem. If you got here by "
               "accident (perhaps by trying to see what --pdb does), "
               "you can get out with 'quit'.\n\n")
        print("\n{}\n\n".format("\n".join(textwrap.wrap(msg))))
        pdb.post_mortem()
        sys.exit(2)


if __name__ == "__main__":
    main()
