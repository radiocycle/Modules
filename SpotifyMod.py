#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
#
# You CANNOT edit, distribute or redistribute this file without direct permission from the author.
#
# ORIGINAL MODULE: https://raw.githubusercontent.com/hikariatama/ftg/master/spotify.py
# meta developer: @cachedfiles
# requires: telethon spotipy

import asyncio
import contextlib
import functools
import logging
import time
import traceback
from types import FunctionType

import spotipy
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
logging.getLogger("spotipy").setLevel(logging.CRITICAL)


@loader.tds
class SpotifyMod(loader.Module):
    """Card with the currently playing track on Spotify. Idea: t.me/fuccsoc. Implementation: t.me/hikariatama. Developer channel: t.me/hikarimods"""

    strings = {
        "name": "SpotifyMod",
        "need_auth": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Please execute"
            " </b><code>.sauth</code><b> before performing this action.</b>"
        ),
        "err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>An error occurred."
            " Make sure music is playing!</b>\n<code>{}</code>"
        ),
        "already_authed": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Already authorized</b>"
        ),
        "authed": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Authentication"
            " successful</b>"
        ),
        "deauth": (
            "<emoji document_id=5877341274863832725>🚪</emoji> <b>Successfully logged out"
            " of account</b>"
        ),
        "auth": (
            '<emoji document_id=5778168620278354602>🔗</emoji> <a href="{}">Follow this'
            " link</a>, allow access, then enter <code>.scode https://...</code> with"
            " the link you received."
        ),
        "no_music": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>No music is playing!</b>"
        ),
        "currently_on": "Listening on",
        "playlist": "Playlist",
        "owner": "Owner",
        "now_playing": "Now playing",
        "artist": "Artist(s)",
        "album": "Album",
        "duration": "Duration",
        "open_on_songlink": "Open on song.link",
    }

    strings_ru = {
        "_cls_doc": "Карточка с играющим треком в Spotify. Идея: t.me/fuccsoc. Разработка: t.me/hikariatama. Канал разработчика: t.me/hikarimods",
        "need_auth": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Выполни"
            " </b><code>.sauth</code><b> перед выполнением этого действия.</b>"
        ),
        "err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Произошла ошибка."
            " Убедитесь, что музыка играет!</b>\n<code>{}</code>"
        ),
        "already_authed": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Уже авторизован</b>"
        ),
        "authed": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Успешная"
            " аутентификация</b>"
        ),
        "deauth": (
            "<emoji document_id=5877341274863832725>🚪</emoji> <b>Успешный выход из"
            " аккаунта</b>"
        ),
        "auth": (
            '<emoji document_id=5778168620278354602>🔗</emoji> <a href="{}">Пройдите по этой'
            " ссылке</a>, разрешите вход, затем введите <code>.scode https://...</code> с"
            " ссылкой которую вы получили."
        ),
        "no_music": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Музыка не играет!</b>"
        ),
        "currently_on": "Cлушаю на",
        "playlist": "Плейлист",
        "owner": "Владелец",
        "now_playing": "Сейчас играет",
        "artist": "Автор(ы)",
        "album": "Альбом",
        "duration": "Длительность",
        "open_on_songlink": "Открыть на song.link",
    }

    def __init__(self):
        self._client_id = "e0708753ab60499c89ce263de9b4f57a"
        self._client_secret = "80c927166c664ee98a43a2c0e2981b4a"
        self.scope = (
            "user-read-playback-state playlist-read-private playlist-read-collaborative"
            " app-remote-control user-modify-playback-state user-library-modify"
            " user-library-read"
        )
        self.sp_auth = spotipy.oauth2.SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            redirect_uri="https://thefsch.github.io/spotify/",
            scope=self.scope,
        )

    async def client_ready(self, client, db):
        self.font_ready = asyncio.Event()

        self._premium = getattr(await client.get_me(), "premium", False)
        try:
            self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        except Exception:
            self.set("acs_tkn", None)
            self.sp = None

        with contextlib.suppress(Exception):
            await utils.dnd(client, "@DirectLinkGenerator_Bot", archive=True)

    def tokenized(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if not args[0].get("acs_tkn", False) or not args[0].sp:
                await utils.answer(args[1], args[0].strings("need_auth"))
                return

            return await func(*args, **kwargs)

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    def error_handler(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.exception(traceback.format_exc())
                with contextlib.suppress(Exception):
                    await utils.answer(
                        args[1],
                        args[0].strings("err").format(traceback.format_exc()),
                    )

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped


    @error_handler
    @loader.command(
        ru_doc="- Получить ссылку для авторизации"
    )
    async def sauthcmd(self, message: Message):
        """- Get authorization link"""
        if self.get("acs_tkn", False) and not self.sp:
            await utils.answer(message, self.strings("already_authed"))
        else:
            self.sp_auth.get_authorize_url()
            await utils.answer(
                message,
                self.strings("auth").format(self.sp_auth.get_authorize_url()),
            )

    @error_handler
    @loader.command(
        ru_doc="- Вставить код авторизации"
    )
    async def scodecmd(self, message: Message):
        """- Paste authorization code"""
        url = message.message.split(" ")[1]
        code = self.sp_auth.parse_auth_response_url(url)
        self.set("acs_tkn", self.sp_auth.get_access_token(code, True, False))
        self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        await utils.answer(message, self.strings("authed"))

    @error_handler
    @loader.command(
        ru_doc="- Выйти из аккаунта"
    )
    async def unauthcmd(self, message: Message):
        """- Log out of account"""
        self.set("acs_tkn", None)
        del self.sp
        await utils.answer(message, self.strings("deauth"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- Обновить токен авторизации"
    )
    async def stokrefreshcmd(self, message: Message):
        """- Refresh authorization token"""
        self.set(
            "acs_tkn",
            self.sp_auth.refresh_access_token(self.get("acs_tkn")["refresh_token"]),
        )
        self.set("NextRefresh", time.time() + 45 * 60)
        self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        await utils.answer(message, self.strings("authed"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 🎧 Показать карточку играющего трека"
    )
    async def snowcmd(self, message: Message):
        """- 🎧 View current track card."""
        current_playback = self.sp.current_playback()

        if not current_playback or not current_playback.get("is_playing", False):
            await utils.answer(message, self.strings("no_music"))
            return
        
        try:
            device = current_playback["device"]["name"]
        except Exception:
            device = None

        icon = (
            "<emoji document_id=5967816500415827773>💻</emoji>"
            if "computer" in device
            else "<emoji document_id=5872980989705196227>📱</emoji>"
        )

        try:
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = self.sp.playlist(playlist_id)
            playlist_name = playlist.get("name", None)
            try:
                playlist_owner = (
                    f'<a href="https://open.spotify.com/user/{playlist["owner"]["id"]}">{playlist["owner"]["display_name"]}</a>'
                )
            except KeyError:
                playlist_owner = None
        except Exception:
            playlist_name = None
            playlist_owner = None

        try:
            track = current_playback["item"]["name"]
            track_id = current_playback["item"]["id"]
            album_name = current_playback["item"]["album"].get("name", "Unknown Album")
        except Exception:
            await utils.answer(message, self.strings("no_music"))
            return

        track_url = (
            current_playback.get("item", {})
            .get("external_urls", {})
            .get("spotify", None)
        )
        universal_link = f"https://song.link/s/{track_id}"

        artists = [
            artist["name"]
            for artist in current_playback.get("item", {}).get("artists", [])
            if "name" in artist
        ]

        result = (
            "<emoji document_id=5294137402430858861>🎵</emoji> <b>SpotifyMod</b>"
        )
        result += (
            (
                f"\n\n<emoji document_id=6007938409857815902>🎧</emoji> <b>{self.strings('now_playing')}:</b>"
                f" <code>{utils.escape_html(track)}</code>"
                f"\n<emoji document_id=5879770735999717115>👤</emoji> <b>{self.strings('artist')}:</b> <code>{utils.escape_html(', '.join(artists))}</code>"
                if artists
                else (
                    f"<emoji document_id=5870794890006237381>🎶</emoji> <b>{self.strings('now_playing')}:</b>"
                    f" <code>{utils.escape_html(track)}</code>"
                )
            )
            if track
            else ""
        )
        result += (
            f"\n<emoji document_id=5870570722778156940>💿</emoji> <b>{self.strings('album')}:</b>"
            f" <code>{utils.escape_html(album_name)}</code>"
            if album_name
            else ""
        )
        if "duration_ms" in current_playback["item"]:
            duration = current_playback["item"]["duration_ms"] // 1000
            current_second = current_playback.get("progress_ms", 0) // 1000
            minutes = duration // 60
            seconds = duration % 60
            mins = current_second // 60
            secs = current_second % 60
            result += (
                f"\n<emoji document_id=5872756762347573066>🕒</emoji> <b>{self.strings('duration')}:</b>"
                f" <code>{mins}:{secs:02}</code> / <code>{minutes}:{seconds:02}</code>"
            )

        result += (
            "\n\n<emoji document_id=5877307202888273539>📁</emoji>"
            f" <b>{self.strings('playlist')}</b>: <a"
            f' href="https://open.spotify.com/playlist/{playlist_id}">{playlist_name}</a>'
            if playlist_name and playlist_id
            else ""
        )
        result += (
            "\n<emoji document_id=5879770735999717115>👤</emoji>"
            f" <b>{self.strings('owner')}</b>: {playlist_owner}"
            if playlist_owner
            else ""
        )
        result += (
            f"\n{icon} <b>{self.strings('currently_on')}</b>"
            f" <code>{device}</code>"
            if device
            else ""
        )
        if universal_link:
            result += (
                f'\n<emoji document_id=5877465816030515018>🔗</emoji> <b><a href="{universal_link}">{self.strings("open_on_songlink")}</a></b>'
            )

        await utils.answer(message, result)

    async def watcher(self, message: Message):
        """Watcher is used to update token"""
        if not self.sp:
            return

        if self.get("NextRefresh", False):
            ttc = self.get("NextRefresh", 0)
            crnt = time.time()
            if ttc < crnt:
                self.set(
                    "acs_tkn",
                    self.sp_auth.refresh_access_token(
                        self.get("acs_tkn")["refresh_token"]
                    ),
                )
                self.set("NextRefresh", time.time() + 45 * 60)
                self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        else:
            self.set(
                "acs_tkn",
                self.sp_auth.refresh_access_token(self.get("acs_tkn")["refresh_token"]),
            )
            self.set("NextRefresh", time.time() + 45 * 60)
            self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])