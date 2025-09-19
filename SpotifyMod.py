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
# meta developer: @cachedfiles, @kamekuro_hmods, @extracli
# requires: telethon spotipy pillow requests

import asyncio
import contextlib
import functools
import io
import logging
import textwrap
import time
import traceback
from types import FunctionType

import requests
import spotipy
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
logging.getLogger("spotipy").setLevel(logging.CRITICAL)


@loader.tds
class SpotifyMod(loader.Module):
    """Card with the currently playing track on Spotify. Idea: t.me/fuccsoc. Implementation: t.me/hikariatama. Developer channel: t.me/hikarimods. Banners from YaMusic by @kamekuro_hmods"""

    strings = {
        "name": "SpotifyMod",
        "need_auth": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Please execute"
            " </b><code>.sauth</code><b> before performing this action.</b>"
        ),
        "on-repeat": (
            "<emoji document_id=5258420634785947640>🔄</emoji> <b>Set on-repeat.</b>"
        ),
        "off-repeat": (
            "<emoji document_id=5260687119092817530>🔄</emoji> <b>Stopped track"
            " repeat.</b>"
        ),
        "skipped": (
            "<emoji document_id=6037622221625626773>➡️</emoji> <b>Skipped track.</b>"
        ),
        "playing": "<emoji document_id=5773626993010546707>▶️</emoji> <b>Playing...</b>",
        "back": (
            "<emoji document_id=6039539366177541657>⬅️</emoji> <b>Switched to previous"
            " track</b>"
        ),
        "paused": "<emoji document_id=5774077015388852135>❌</emoji> <b>Pause</b>",
        "restarted": (
            "<emoji document_id=5843596438373667352>✅️</emoji> <b>Playing track"
            " from the"
            " beginning</b>"
        ),
        "liked": (
            "<emoji document_id=5258179403652801593>❤️</emoji> <b>Liked current"
            " playback</b>"
        ),
        "unlike": (
            "<emoji document_id=5774077015388852135>❌</emoji>"
            " <b>Unliked current playback</b>"
        ),
        "err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>An error occurred."
            "</b>\n<code>{}</code>"
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
        "dl_err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Failed to download"
            " track.</b>"
        ),
        "volume_changed": (
            "<emoji document_id=5890997763331591703>🔊</emoji>"
            " <b>Volume changed to {}%.</b>"
        ),
        "volume_invalid": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Volume level must be"
            " a number between 0 and 100.</b>"
        ),
        "volume_err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>An error occurred while"
            " changing volume.</b>"
        ),
        "no_volume_arg": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Please specify a"
            " volume level between 0 and 100.</b>"
        ),
        "searching_tracks": (
            "<emoji document_id=5841359499146825803>🕔</emoji> <b>Searching for tracks"
            " matching {}...</b>"
        ),
        "no_search_query": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Please specify a"
            " search query.</b>"
        ),
        "no_tracks_found": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>No tracks found for"
            " {}.</b>"
        ),
        "search_results": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Search results for"
            " {}:</b>\n\n{}"
        ),
        "downloading_search_track": (
            "<emoji document_id=5841359499146825803>🕔</emoji> <b>Downloading {}...</b>"
        ),
        "download_success": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Successfully downloaded {}.</b>"
        ),
        "invalid_track_number": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Invalid track number."
            " Please search first or provide a valid number from the list.</b>"
        ),
        "device_list": (
            "<emoji document_id=5956561916573782596>📄</emoji> <b>Available devices:</b>\n{}"
        ),
        "no_devices_found": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>No devices found.</b>"
        ),
        "device_changed": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Playback transferred to"
            " {}.</b>"
        ),
        "invalid_device_id": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Invalid device ID."
            " Use</b> <code>.sdevice</code> <b>to see available devices.</b>"
        ),
        "search_results_cleared": "<emoji document_id=5776375003280838798>✅</emoji> <b>Search results cleared</b>",
    }

    strings_ru = {
        "_cls_doc": "Карточка с играющим треком в Spotify. Идея: t.me/fuccsoc. Разработка: t.me/hikariatama. Канал разработчика: t.me/hikarimods. Баннеры из YaMusic от @kamekuro_hmods",
        "need_auth": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Выполни"
            " </b><code>.sauth</code><b> перед выполнением этого действия.</b>"
        ),
        "err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Произошла ошибка."
            "</b>\n<code>{}</code>"
        ),
        "on-repeat": (
            "<emoji document_id=5258420634785947640>🔄</emoji> <b>Включен повтор трека.</b>"
        ),
        "off-repeat": (
            "<emoji document_id=5260687119092817530>🔄</emoji> <b>Повтор трека отключён.</b>"
        ),
        "skipped": (
            "<emoji document_id=6037622221625626773>➡️</emoji> <b>Трек пропущен.</b>"
        ),
        "playing": "<emoji document_id=5773626993010546707>▶️</emoji> <b>Играет...</b>",
        "back": (
            "<emoji document_id=6039539366177541657>⬅️</emoji> <b>Переключено на предыдущий трек</b>"
        ),
        "paused": "<emoji document_id=5774077015388852135>❌</emoji> <b>Пауза</b>",
        "restarted": (
            "<emoji document_id=5843596438373667352>✅️</emoji> <b>Воспроизведение трека с начала...</b>"
        ),
        "liked": (
            "<emoji document_id=5258179403652801593>❤️</emoji> <b>Текущий трек добавлен в избранное</b>"
        ),
        "unlike": (
            "<emoji document_id=5774077015388852135>❌</emoji> <b>Убрал лайк с текущего трека</b>"
        ),
        "already_authed": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Уже авторизован</b>"
        ),
        "authed": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Успешная аутентификация</b>"
        ),
        "deauth": (
            "<emoji document_id=5877341274863832725>🚪</emoji> <b>Успешный выход из аккаунта</b>"
        ),
        "auth": (
            '<emoji document_id=5778168620278354602>🔗</emoji> <a href="{}">Пройдите по этой ссылке</a>, разрешите вход, затем введите <code>.scode https://...</code> с ссылкой которую вы получили.'
        ),
        "no_music": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Музыка не играет!</b>"
        ),
        "dl_err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Не удалось скачать трек.</b>"
        ),
        "volume_changed": (
            "<emoji document_id=5890997763331591703>🔊</emoji>"
            " <b>Громкость изменена на {}%.</b>"
        ),
        "volume_invalid": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Уровень громкости должен"
            " быть числом от 0 до 100.</b>"
        ),
        "volume_err": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Произошла ошибка при"
            " изменении громкости.</b>"
        ),
        "no_volume_arg": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Пожалуйста, укажите"
            " уровень громкости от 0 до 100.</b>"
        ),
        "searching_tracks": (
            "<emoji document_id=5841359499146825803>🕔</emoji> <b>Идет поиск треков"
            " по запросу {}...</b>"
        ),
        "no_search_query": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Пожалуйста, укажите"
            " поисковый запрос.</b>"
        ),
        "no_tracks_found": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>По запросу '{}'"
            " ничего не найдено.</b>"
        ),
        "search_results": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Результаты поиска"
            " по запросу {}:</b>\n\n{}"
        ),
        "downloading_search_track": (
            "<emoji document_id=5841359499146825803>🕔</emoji> <b>Скачиваю {}...</b>"
        ),
        "download_success": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Трек {} успешно скачан.</b>"
        ),
        "invalid_track_number": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Некорректный номер трека."
            " Сначала выполните поиск или укажите правильный номер из списка.</b>"
        ),
        "device_list": (
            "<emoji document_id=5956561916573782596>📄</emoji> <b>Доступные устройства:</b>\n{}"
        ),
        "no_devices_found": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Устройства не найдены.</b>"
        ),
        "device_changed": (
            "<emoji document_id=5776375003280838798>✅</emoji> <b>Воспроизведение переключено на"
            " {}.</b>"
        ),
        "invalid_device_id": (
            "<emoji document_id=5778527486270770928>❌</emoji> <b>Некорректный ID устройства."
            " Используйте</b> <code>.sdevice</code> <b>, чтобы увидеть доступные устройства.</b>"
        ),
        "search_results_cleared": "<emoji document_id=5776375003280838798>✅</emoji> <b>Результаты поиска очищены</b>",
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
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "show_banner",
                True,
                "Show banner with track info",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_text",
                (
                    "<emoji document_id=6007938409857815902>🎧</emoji> <b>Now playing:</b> {track} — {artists}\n"
                    "<emoji document_id=5877465816030515018>🔗</emoji> <b><a href='{songlink}'>song.link</a></b>"
                ),
                """Custom text, supports {track}, {artists}, {album}, {playlist}, {playlist_owner}, {spotify_url}, {songlink}, {progress}, {duration}, {device} placeholders""",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "banner_gen_text",
                "<emoji document_id=5841359499146825803>🕔</emoji> <i>Generating banner...</i>",
                "Custom banner generation text",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "download_track_text",
                "<emoji document_id=5841359499146825803>🕔</emoji> <i>Downloading track...</i>",
                "Custom download text for snowt",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "title_font",
                "https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Bold.ttf",
                "Custom font for title. Specify URL to .ttf file",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "artists_font",
                "https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Regular.ttf",
                "Custom font for artists. Specify URL to .ttf file",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "time_font",
                "https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Bold.ttf",
                "Custom font for time. Specify URL to .ttf file",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "search_result_text",
                "<b>{number}.</b> {track_name} — {artists}\n<a href='{track_url}'>🔗 Spotify</a>",
                """Custom text for a single search result. Supports {number}, {track_name}, {artists}, {track_url} placeholders""",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "downloaded_search_track",
                "<emoji document_id=5776375003280838798>✅</emoji> <b>Successfully downloaded</b> {track} — {artists}",
                """Custom text for a single search result. Supports {track}, {artists} placeholders""",
                validator=loader.validators.String(),
            ),
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

        with contextlib.suppress(Exception):
            await utils.dnd(client, "@LosslessRobot", archive=True)

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

    def _create_banner(
        self,
        title: str, artists: list,
        duration: int, progress: int,
        track_cover: bytes
    ):
        w, h = 1920, 768
        title_font = ImageFont.truetype(io.BytesIO(requests.get(
            self.config["title_font"]
        ).content), 80)
        art_font = ImageFont.truetype(io.BytesIO(requests.get(
            self.config["artists_font"]
        ).content), 55)
        time_font = ImageFont.truetype(io.BytesIO(requests.get(
            self.config["time_font"]
        ).content), 36)

        track_cov = Image.open(io.BytesIO(track_cover)).convert("RGBA")
        banner = track_cov.resize((w, w)).crop(
            (0, (w-h)//2, w, ((w-h)//2)+h)
        ).filter(ImageFilter.GaussianBlur(radius=14))
        banner = ImageEnhance.Brightness(banner).enhance(0.3)

        track_cov = track_cov.resize((banner.size[1]-150, banner.size[1]-150))
        mask = Image.new("L", track_cov.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, track_cov.size[0], track_cov.size[1]), radius=35, fill=255)
        track_cov.putalpha(mask)
        track_cov = track_cov.crop(track_cov.getbbox())
        banner.paste(track_cov, (75, 75), mask)

        title_lines = textwrap.wrap(title, 23)
        if len(title_lines) > 1:
            title_lines[1] = title_lines[1] + "..." if len(title_lines) > 2 else title_lines[1]
        title_lines = title_lines[:2]
        artists_lines = textwrap.wrap(", ".join(artists), width=40)
        if len(artists_lines) > 1:
            for index, art in enumerate(artists_lines):
                if "," in art[-2:]:
                    artists_lines[index] = art[:art.rfind(",") - 1]

        draw = ImageDraw.Draw(banner)
        x, y = 150+track_cov.size[0], 110
        for index, line in enumerate(title_lines):
            draw.text((x, y), line, font=title_font, fill="#FFFFFF")
            if index != len(title_lines)-1:
                y += 70
        x, y = 150+track_cov.size[0], 110*2
        if len(title_lines) > 1: y += 70
        for index, line in enumerate(artists_lines):
            draw.text((x, y), line, font=art_font, fill="#A0A0A0")
            if index != len(artists_lines)-1:
                y += 50

        draw.rounded_rectangle([768, 650, 768+1072, 650+15], radius=15//2, fill="#A0A0A0")
        if duration > 0:
             draw.rounded_rectangle([768, 650, 768+int(1072*(progress/duration)), 650+15], radius=15//2, fill="#FFFFFF")
        draw.text((768, 600), f"{(progress//1000//60):02}:{(progress//1000%60):02}", font=time_font, fill="#FFFFFF")
        draw.text((1745, 600), f"{(duration//1000//60):02}:{(duration//1000%60):02}", font=time_font, fill="#FFFFFF")

        by = io.BytesIO()
        banner.save(by, format="PNG"); by.seek(0)
        by.name = "banner.png"
        return by

    async def _dl_track(self, client, track: str, artists: str):
        query = f"{track} - {artists}"
        async with client.conversation("@LosslessRobot") as conv:
            await conv.send_message(query)
            response = await conv.get_response()
            candidate_pos = None
            if response.buttons:
                for i, row in enumerate(response.buttons):
                    for j, button in enumerate(row):
                        button_text = button.text.lower()
                        if track.lower() in button_text and artists.lower() in button_text:
                            candidate_pos = (i, j)
                            break
                    if candidate_pos:
                        break
                if candidate_pos is None:
                    candidate_pos = (0, 0)
                await response.click(*candidate_pos)
                track_msg = await conv.get_response()
                return track_msg
            return None

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 🔊 Изменить громкость. .svolume <0-100>"
    )
    async def svolume(self, message: Message):
        """🔊 Change playback volume. .svolume <0-100>"""
        try:
            args = utils.get_args_raw(message)
            if not args:
                await utils.answer(message, self.strings("no_volume_arg"))
                return

            volume_percent = int(args)
            if 0 <= volume_percent <= 100:
                self.sp.volume(volume_percent)
                await utils.answer(message, self.strings("volume_changed").format(volume_percent))
            else:
                await utils.answer(message, self.strings("volume_invalid"))
        except ValueError:
            await utils.answer(message, self.strings("volume_invalid"))
        except Exception:
            await utils.answer(message, self.strings("volume_err"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc=(
            "- 🎵 Выбрать устройство для воспроизведения. Например: .sdevice <ID устройства>\n"
            "- 📝 Показать список устройств: .sdevice"
        )
    )
    async def sdevicecmd(self, message: Message):
        """🎵 Set preferred playback device. Usage: .sdevice <device_id> or .sdevice to list devices"""
        args = utils.get_args_raw(message)
        devices = self.sp.devices()["devices"]

        if not args:
            if not devices:
                await utils.answer(message, self.strings("no_devices_found"))
                return

            device_list_text = ""
            for i, device in enumerate(devices):
                is_active = "(active)" if device["is_active"] else ""
                device_list_text += (
                    f"<b>{i+1}.</b> {device['name']}"
                    f" ({device['type']}) {is_active}\n"
                )

            await utils.answer(message, self.strings("device_list").format(device_list_text.strip()))
            return

        device_id = None
        try:
            device_number = int(args)
            if 0 < device_number <= len(devices):
                device_id = devices[device_number - 1]["id"]
                device_name = devices[device_number - 1]["name"]
            else:
                await utils.answer(message, self.strings("invalid_device_id"))
                return
        except ValueError:
            found_device = next((d for d in devices if d["id"] == args.strip()), None)
            if found_device:
                device_id = found_device["id"]
                device_name = found_device["name"]
            else:
                await utils.answer(message, self.strings("invalid_device_id"))
                return

        self.sp.transfer_playback(device_id=device_id)
        await utils.answer(message, self.strings("device_changed").format(device_name))
            
    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 💫 Включить повтор трека"
    )
    async def srepeatcmd(self, message: Message):
        """💫 Repeat"""
        self.sp.repeat("track")
        await utils.answer(message, self.strings("on-repeat"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- ✋ Остановить повтор"
    )
    async def sderepeatcmd(self, message: Message):
        """✋ Stop repeat"""
        self.sp.repeat("context")
        await utils.answer(message, self.strings("off-repeat"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 👉 Следующий трек"
    )
    async def snextcmd(self, message: Message):
        """👉 Next track"""
        self.sp.next_track()
        await utils.answer(message, self.strings("skipped"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 🤚 Продолжить воспроизведение"
    )
    async def sresumecmd(self, message: Message):
        """- 🤚 Resume"""
        self.sp.start_playback()
        await utils.answer(message, self.strings("playing"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 🤚 Пауза"
    )
    async def spausecmd(self, message: Message):
        """- 🤚 Pause"""
        self.sp.pause_playback()
        await utils.answer(message, self.strings("paused"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- ⏮ Предыдущий трек"
    )
    async def sbackcmd(self, message: Message):
        """- ⏮ Previous track"""
        self.sp.previous_track()
        await utils.answer(message, self.strings("back"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- ⏪ Перезапустить трек"
    )
    async def sbegincmd(self, message: Message):
        """- ⏪ Restart track"""
        self.sp.seek_track(0)
        await utils.answer(message, self.strings("restarted"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- ❤️ Лайкнуть играющий трек"
    )
    async def slikecmd(self, message: Message):
        """- ❤️ Like current track"""
        cupl = self.sp.current_playback()
        self.sp.current_user_saved_tracks_add([cupl["item"]["id"]])
        await utils.answer(message, self.strings("liked"))
    
    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 💔 Убрать лайк с играющего трека"
    )
    async def sunlikecmd(self, message: Message):
        """- 💔 Unlike current track"""
        cupl = self.sp.current_playback()
        self.sp.current_user_saved_tracks_delete([cupl["item"]["id"]])
        await utils.answer(message, self.strings("unlike"))

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

        track = current_playback["item"]["name"]
        track_id = current_playback["item"]["id"]
        artists = ", ".join([a["name"] for a in current_playback["item"]["artists"]])
        album_name = current_playback["item"]["album"].get("name", "Unknown Album")
        duration_ms = current_playback["item"].get("duration_ms", 0)
        progress_ms = current_playback.get("progress_ms", 0)

        duration = f"{duration_ms//1000//60}:{duration_ms//1000%60:02}"
        progress = f"{progress_ms//1000//60}:{progress_ms//1000%60:02}"

        spotify_url = f"https://open.spotify.com/track/{track_id}"
        songlink = f"https://song.link/s/{track_id}"

        try:
            device_raw = (
                current_playback["device"]["name"]
                + " "
                + current_playback["device"]["type"].lower()
            )
            device = device_raw.replace("computer", "").replace("smartphone", "").strip()
        except Exception:
            device = None

        try:
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = self.sp.playlist(playlist_id)
            playlist_name = playlist.get("name", None)
            try:
                playlist_owner = (
                    f'<a href="https://open.spotify.com/user/{playlist["owner"]["id"]}">'
                    f'{playlist["owner"]["display_name"]}</a>'
                )
            except KeyError:
                playlist_owner = playlist.get("owner", {}).get("display_name", "")
        except Exception:
            playlist_name = ""
            playlist_owner = ""

        text = self.config["custom_text"].format(
            track=utils.escape_html(track),
            artists=utils.escape_html(artists),
            album=utils.escape_html(album_name),
            duration=duration,
            progress=progress,
            device=device,
            spotify_url=spotify_url,
            songlink=songlink,
            playlist=utils.escape_html(playlist_name) if playlist_name else "",
            playlist_owner=playlist_owner or "",
        )

        if self.config["show_banner"]:
            cover_url = current_playback["item"]["album"]["images"][0]["url"]
            cover_bytes = await utils.run_sync(requests.get, cover_url)

            tmp_msg = await utils.answer(message, text + f'\n\n{self.config["banner_gen_text"]}')

            banner_file = await utils.run_sync(
                self._create_banner,
                title=track,
                artists=[a["name"] for a in current_playback["item"]["artists"]],
                duration=duration_ms,
                progress=progress_ms,
                track_cover=cover_bytes.content,
            )
            await utils.answer(tmp_msg, text, file=banner_file)
        else:
            await utils.answer(message, text)

    @error_handler
    @tokenized
    @loader.command(
        ru_doc="- 🎧 Скачать играющий трек"
    )
    async def snowtcmd(self, message: Message):
        """- 🎧 Download current track."""
        current_playback = self.sp.current_playback()
        if not current_playback or not current_playback.get("is_playing", False):
            await utils.answer(message, self.strings("no_music"))
            return

        track = current_playback["item"]["name"]
        artists = ", ".join([a["name"] for a in current_playback["item"]["artists"]])
        album_name = current_playback["item"]["album"].get("name", "Unknown Album")
        duration_ms = current_playback["item"].get("duration_ms", 0)
        progress_ms = current_playback.get("progress_ms", 0)

        duration = f"{duration_ms//1000//60}:{duration_ms//1000%60:02}"
        progress = f"{progress_ms//1000//60}:{progress_ms//1000%60:02}"

        spotify_url = f"https://open.spotify.com/track/{current_playback['item']['id']}"
        songlink = f"https://song.link/s/{current_playback['item']['id']}"

        try:
            device_raw = (
                current_playback["device"]["name"]
                + " "
                + current_playback["device"]["type"].lower()
            )
            device = device_raw.replace("computer", "").replace("smartphone", "").strip()
        except Exception:
            device = None

        try:
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = self.sp.playlist(playlist_id)
            playlist_name = playlist.get("name", None)
            try:
                playlist_owner = (
                    f'<a href="https://open.spotify.com/user/{playlist["owner"]["id"]}">'
                    f'{playlist["owner"]["display_name"]}</a>'
                )
            except KeyError:
                playlist_owner = playlist.get("owner", {}).get("display_name", "")
        except Exception:
            playlist_name = ""
            playlist_owner = ""

        text = self.config["custom_text"].format(
            track=utils.escape_html(track),
            artists=utils.escape_html(artists),
            album=utils.escape_html(album_name),
            duration=duration,
            progress=progress,
            device=device,
            spotify_url=spotify_url,
            songlink=songlink,
            playlist=utils.escape_html(playlist_name) if playlist_name else "",
            playlist_owner=playlist_owner or "",
        )

        msg = await utils.answer(message, text + f'\n\n{self.config["download_track_text"]}')
        track_msg = await self._dl_track(message.client, track, artists)

        if (
            track_msg
            and track_msg.media
            and hasattr(track_msg.media, "document")
            and getattr(track_msg.media.document, "mime_type", "").startswith("audio/")
        ):
            await utils.answer(msg, text, file=track_msg.media)
        else:
            await utils.answer(msg, self.strings("dl_err"))

    @error_handler
    @tokenized
    @loader.command(
        ru_doc=(
            "- 🔍 Поиск треков. Например: .ssearch Imagine Dragons Believer\n"
            "- 🎧 Скачать трек: .ssearch 1 (где 1 — номер трека из списка)"
        )
    )
    async def ssearchcmd(self, message: Message):
        """🔍 Search for tracks. Usage: .ssearch <query> or .ssearch <number> to download"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_search_query"))
            return

        try:
            track_number = int(args)
            search_results = self.get("last_search_results", [])
            if not search_results or track_number <= 0 or track_number > len(search_results):
                raise ValueError

            msg = await utils.answer(message, f'{self.config["download_track_text"]}')
            track_info = search_results[track_number - 1]
            track_name = track_info["name"]
            artists = ", ".join([a["name"] for a in track_info["artists"]])
            
            track_msg = await self._dl_track(message.client, track_name, artists)
            
            if not track_msg:
                return

            await utils.answer(
                msg,
                self.config["downloaded_search_track"].format(
                    track=track_name,
                    artists=artists,
                ),
                file=track_msg.media,
            )

            return
        except ValueError:
            await utils.answer(message, self.strings("searching_tracks").format(args))

            results = self.sp.search(q=args, limit=5, type="track")

            if not results or not results["tracks"]["items"]:
                await utils.answer(message, self.strings("no_tracks_found").format(args))
                return

            self.set("last_search_results", results["tracks"]["items"])
            
            tracks_list = []
            for i, track in enumerate(results["tracks"]["items"]):
                track_name = track["name"]
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                track_url = track["external_urls"]["spotify"]
                tracks_list.append(
                    self.config["search_result_text"].format(
                        number=i + 1,
                        track_name=utils.escape_html(track_name),
                        artists=utils.escape_html(artists),
                        track_url=track_url,
                    )
                )

            text = "\n".join(tracks_list)
            await utils.answer(message, self.strings("search_results").format(args, text))
    
    @loader.command(
        ru_doc="- 🔄 Сброс результатов поиска по трекам"
    )
    async def ssearchresetcmd(self, message: Message):
        """- 🔄 Reset track search results"""
        self.set("last_search_results", [])
        await utils.answer(message, self.strings["search_results_cleared"])

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
