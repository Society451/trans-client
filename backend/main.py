import asyncio
import time
import webview
import os
from trans import translate_text

class Api:
    async def translate_async(self, text, src_lang, dest_lang):
        start_time = time.time()
        translated_text = await translate_text(text, src_lang, dest_lang)
        end_time = time.time()
        return {
            'translated_text': translated_text,
            'time_taken': end_time - start_time
        }
    
    def translate(self, text, src_lang, dest_lang):
        return asyncio.run(self.translate_async(text, src_lang, dest_lang))

def main():
    api = Api()
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/main.html'))
    window = webview.create_window('Translator', f'file://{html_path}', js_api=api)
    webview.start()

if __name__ == '__main__':
    main()
