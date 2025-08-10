# meta developer: @cachedfiles

import requests
import asyncio
import logging
import traceback
from logging import basicConfig
from .. import loader, utils

basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@loader.tds
class RandomAnimePicMod(loader.Module):
  strings = {
    "name": "RandomAnimePic",
    "img": "<emoji document_id=4916036072560919511>✅</emoji> <b>Your anime pic</b>\n<emoji document_id=5877465816030515018>🔗</emoji> <b>URL:</b> {}",
    "loading": "<emoji document_id=4911241630633165627>✨</emoji> <b>Loading image...</b>",
    "error": "<emoji document_id=5116151848855667552>🚫</emoji> <b>An unexpected error occurred...</b>",
  }
  
  strings_ru = {
    "img": "<emoji document_id=4916036072560919511>✅</emoji> <b>Ваша аниме-картинка</b>\n<emoji document_id=5877465816030515018>🔗</emoji> <b>Ссылка:</b> {}",
    "loading": "<emoji document_id=4911241630633165627>✨</emoji> <b>Загрузка изображения...</b>",
    "error": "<emoji document_id=5116151848855667552>🚫</emoji> <b>Произошла непредвиденная ошибка...</b>",
  }
  
  @loader.command(
    ru_doc="- получить рандомную аниме-картинку 👀"
  )
  async def rapiccmd(self, message):
    """- fetch random anime-pic 👀"""
    
    await utils.answer(message, self.strings("loading"))

    try:
      res = requests.get("https://api.nekosia.cat/api/v1/images/cute?count=1")
      res.raise_for_status()
      data = res.json()
      image_url = data['image']['original']['url']
      
      await asyncio.sleep(2)
      
      await utils.answer(message, self.strings("img").format(image_url), file=image_url, reply_to=message.reply_to_msg_id)
    
    except Exception:
      logger.error("Error fetching random anime pic: %s", traceback.format_exc())

      await utils.answer(message, self.strings("error"))
      
      await asyncio.sleep(5)
