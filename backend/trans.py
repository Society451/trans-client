import asyncio
from googletrans import Translator

async def translate_text(text, src_lang, dest_lang):
    translator = Translator()
    result = await translator.translate(text, src=src_lang, dest=dest_lang)
    return result.text
