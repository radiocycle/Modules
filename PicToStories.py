# =======================================
#   _  __         __  __           _
#  | |/ /___     |  \/  | ___   __| |___
#  | ' // _ \    | |\/| |/ _ \ / _` / __|
#  | . \  __/    | |  | | (_) | (_| \__ \
#  |_|\_\___|    |_|  |_|\___/ \__,_|___/
#           @ke_mods
# =======================================
#
#  LICENSE: CC BY-ND 4.0 (Attribution-NoDerivatives 4.0 International)
#  --------------------------------------
#  https://creativecommons.org/licenses/by-nd/4.0/legalcode
# =======================================

# meta developer: @ke_mods
# requires: pillow

import io
from telethon import functions, types
from .. import loader, utils
from PIL import Image

@loader.tds
class PicToStoriesMod(loader.Module):
    """Grid 3x3 for stories"""
    
    strings = {
        "name": "PicToStories",
        "no_rep": "<emoji document_id=5879813604068298387>❗️</emoji> <b>Reply to photo!</b>",
        "work": "<emoji document_id=5841359499146825803>🕔</emoji> <b>Processing...</b>",
        "done": "<emoji document_id=5776375003280838798>✅</emoji> <b>Done! Check your profile.</b>",
        "err": "<emoji document_id=5778527486270770928>❌</emoji> <b>Error:</b> {}"
    }

    strings_ru = {
        "no_rep": "<emoji document_id=5879813604068298387>❗️</emoji> <b>Реплай на фото!</b>",
        "work": "<emoji document_id=5841359499146825803>🕔</emoji> <b>Обрабатываю...</b>",
        "done": "<emoji document_id=5776375003280838798>✅</emoji> <b>Готово! Проверяй профиль.</b>",
        "err": "<emoji document_id=5778527486270770928>❌</emoji> <b>Ошибка:</b> {}"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.command(ru_doc="<реплай на фото> - Сделать сетку 3x3 в сторис")
    async def ptscmd(self, message):
        """<reply to photo> - make 3x3 grid"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings("no_rep"))
            return

        try:
            b = await reply.download_media(file=bytes)
            img = Image.open(io.BytesIO(b))
        except Exception as e:
            await utils.answer(message, self.strings("err").format(e))
            return

        await utils.answer(message, self.strings("work"))

        w, h = img.size
        
        if abs(w/h - 0.8) > 0.05:
            img = img.resize((w, int(w * 1.25)), Image.LANCZOS)
            w, h = img.size

        parts = []
        pw, ph = w // 3, h // 3
        
        for r in range(3):
            for c in range(3):
                x, y = c * pw, r * ph
                parts.append(img.crop((x, y, x + pw, y + ph)))

        parts.reverse()

        for p in parts:
            out = io.BytesIO()
            p.save(out, "JPEG")
            out.seek(0)
            
            f = await self.client.upload_file(out, file_name="s.jpg")
            
            res = await self.client(functions.stories.SendStoryRequest(
                peer=types.InputPeerSelf(),
                media=types.InputMediaUploadedPhoto(f),
                privacy_rules=[types.InputPrivacyValueAllowAll()]
            ))
            
            try:
                sid = None
                for u in res.updates:
                    if hasattr(u, 'story_id'): sid = u.story_id
                    elif hasattr(u, 'id'): sid = u.id
                    if sid: break
                
                if sid:
                    await self.client(functions.stories.TogglePinnedRequest(
                        peer=types.InputPeerSelf(), id=[sid], pinned=True
                    ))
            except:
                pass

        await utils.answer(message, self.strings("done"))
