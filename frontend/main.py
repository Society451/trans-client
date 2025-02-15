import asyncio
import time
from googletrans import Translator

async def main():
    # Create a Translator object
    translator = Translator()

    # Start the timer
    start_time = time.time()

    # Translate 'hi mom!' to Chinese (Simplified)
    result = await translator.translate('hi mom!', src='en', dest='zh-CN')

    # End the timer
    end_time = time.time()

    # Output the translated text
    print(f'Translated text: {result.text}')
    
    # Output the time taken
    print(f'Time taken: {end_time - start_time} seconds')

# Run the main function
asyncio.run(main())