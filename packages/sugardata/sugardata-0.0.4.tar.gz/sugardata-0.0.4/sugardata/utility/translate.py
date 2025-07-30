import asyncio
from deep_translator import GoogleTranslator
from langdetect import detect


class TranslationUtility:

    @staticmethod
    def translate(text: str, target_language: str="en", source_language: str="auto") -> str:
        try:
            return GoogleTranslator(source=source_language, target=target_language).translate(text)
        except Exception as e:
            print("Error in translating concept: ", e)
            raise e
        
    @staticmethod
    def detect_language(text: str) -> str:
        try:
            return detect(text)
        except Exception as e:
            print("Error in detecting language: ", e)
            raise e
        
    @staticmethod
    async def detect_language_async(text: str) -> str:
        try:
            return await asyncio.to_thread(detect, text)
        except Exception as e:
            print("Error in detecting language asynchronously: ", e)
            raise e