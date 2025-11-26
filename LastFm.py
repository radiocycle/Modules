# ---------------------------------------------------------------------------------
#░█▀▄░▄▀▀▄░█▀▄░█▀▀▄░█▀▀▄░█▀▀▀░▄▀▀▄░░░█▀▄▀█
#░█░░░█░░█░█░█░█▄▄▀░█▄▄█░█░▀▄░█░░█░░░█░▀░█
#░▀▀▀░░▀▀░░▀▀░░▀░▀▀░▀░░▀░▀▀▀▀░░▀▀░░░░▀░░▒▀
# Name: LastFM
# Description: Module for music from different services
# Author: @codrago_m
# ---------------------------------------------------------------------------------
# 🔒    Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# ---------------------------------------------------------------------------------
# Author: @codrago
# Commands: nowplay
# scope: heroku_only
# meta developer: @ke_mods
# meta banner: https://raw.githubusercontent.com/coddrago/modules/refs/heads/main/banner.png
# meta pic: https://envs.sh/Hob.webp
# ---------------------------------------------------------------------------------

# Forked from @codrago_m

from .. import loader, utils 
from herokutl import events
import requests
import asyncio
import io
import textwrap
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# Forked from @codrago_m

@loader.tds
class lastfmmod(loader.Module):
    """Module for music from different services. Forked from @codrago_m"""
    
    strings = {
        "name": "LastFm",
        "no_track": "<emoji document_id=5465665476971471368>❌</emoji> <b>No track is currently playing</b>",
        "_doc_text": "The text that will be written next to the file",
        "_doc_username": "Your username from last.fm",
        "nick_error": "<emoji document_id=5465665476971471368>❌</emoji> <b>Put your nickname from last.fm</b>",
    }

    strings_ru = {
        "name": "LastFm",
        "no_track": "<emoji document_id=5465665476971471368>❌</emoji> <b>Сейчас ничего не играет</b>",
        "_doc_text": "Текст, который будет написан рядом с файлом",
        "_doc_username": "Ваш username с last.fm",
        "nick_error": "<emoji document_id=5465665476971471368>❌</emoji> <b>Укажите ваш никнейм с last.fm</b>",
    }
    
# Forked from @codrago_m

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "username",
                None,
                lambda: self.strings["_doc_username"],
            ),
            loader.ConfigValue(
                "custom_text",
                "<emoji document_id=5413612466208799435>🤩</emoji> <b>{song_name}</b> — <b>{song_artist}</b>",
                lambda: self.strings["_doc_text"],
            ),
        )

# Forked from @codrago_m

    def _create_banner(
        self,
        title: str,
        artists: str,
        track_cover: bytes
    ):
        w, h = 1920, 768
        
        font_bytes = requests.get("https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Bold.ttf").content
        
        title_font = ImageFont.truetype(io.BytesIO(font_bytes), 80)
        art_font = ImageFont.truetype(io.BytesIO(font_bytes), 60)
        track_cov = Image.open(io.BytesIO(track_cover)).convert("RGBA")
        
        banner = track_cov.resize((w, w)).crop((0, (w-h)//2, w, ((w-h)//2)+h)).filter(ImageFilter.GaussianBlur(radius=14))
        banner = ImageEnhance.Brightness(banner).enhance(0.3)
        
        track_cov = track_cov.resize((banner.size[1]-150, banner.size[1]-150))
        mask = Image.new("L", track_cov.size, 0)
        
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, track_cov.size[0], track_cov.size[1]), radius=35, fill=255)
        
        track_cov.putalpha(mask)
        track_cov = track_cov.crop(track_cov.getbbox())
        
        banner.paste(track_cov, (75, 75), mask)
        
        if len(title) > 20:
            title = title[:20] + "..."
        title_lines = [title]
        if len(artists) > 20:
            artists = artists[:20] + "..."
        artists_lines = [artists]
        
        draw = ImageDraw.Draw(banner)
        cover_end_x = 75 + track_cov.size[0]       
        center_x = cover_end_x + ((w - cover_end_x) // 2)
        y = 280
        
        for line in title_lines:
            line_width = draw.textlength(line, font=title_font)
            x = center_x - (line_width / 2)
            draw.text((x, y), line, font=title_font, fill="#FFFFFF")
            y += 80
        y = 380
        
        for line in artists_lines:
            line_width = draw.textlength(line, font=art_font)
            x = center_x - (line_width / 2)
            draw.text((x, y), line, font=art_font, fill="#A0A0A0")
            y += 50
            
        by = io.BytesIO()
        banner.save(by, format="PNG")
        by.seek(0)
        by.name = "banner.png"
        return by
        
# Forked from @codrago_m

    @loader.command(alias="np")
    async def nowplay(self, message):
        """| send playing track info"""
        lastfm_username = self.config["username"]
        API_KEY = "460cda35be2fbf4f28e8ea7a38580730"
        
        if not lastfm_username:
            response_text = self.strings["nick_error"]
            await self.invoke("config", "lastfm", message=message)
            await utils.answer(message, response_text)
            
        else:
            try:
                current_track_url = f'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&nowplaying=true&user={lastfm_username}&api_key={API_KEY}&format=json'
                response = requests.get(current_track_url)
                data = response.json()
                
                if 'recenttracks' in data and 'track' in data['recenttracks'] and data['recenttracks']['track']:
                    nowplaying_track = None
                    
                    for track in data['recenttracks']['track']:
                        if '@attr' in track and 'nowplaying' in track['@attr']:
                            nowplaying_track = track
                            break
                            
                    if nowplaying_track:
                        song_name = nowplaying_track.get('name', 'Unknown song')
                        song_artist = nowplaying_track.get('artist', {}).get('#text', 'Unknown Artist')
                        
                        response_text = self.config["custom_text"].format(
                            song_artist=song_artist,
                            song_name=song_name
                        )
                        
                        cover_url = None
                        
                        if 'image' in nowplaying_track:
                            for img in nowplaying_track['image']:
                                if img['size'] == 'extralarge':
                                    cover_url = img['#text']
                                    break
                            if not cover_url:
                                cover_url = nowplaying_track['image'][-1]['#text']
                                
                        if cover_url:
                            cover_bytes = await utils.run_sync(requests.get, cover_url)
                            banner_file = await utils.run_sync(
                                self._create_banner,
                                title=song_name,
                                artists=song_artist,
                                track_cover=cover_bytes.content,
                            )
                            await utils.answer(message, response_text, file=banner_file)
                            
                    else:
                        await utils.answer(message, self.strings["no_track"])
                        
                else:
                    await utils.answer(message, self.strings["no_track"])
                    
            except Exception as e:
                await utils.answer(message, f"<pre><code class='language-python'>{e}</code></pre>")
                
# Forked from @codrago_m
