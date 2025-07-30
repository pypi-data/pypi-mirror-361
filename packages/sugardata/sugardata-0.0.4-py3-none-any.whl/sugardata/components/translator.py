

class Translator:
    """
    Supported translation vendors:
    - deep-translator
    - googletrans [manual installation required]
    """

    @staticmethod
    def translate(text: str, target_language: str, source_language: str, vendor: str) -> str:
        if vendor == "deep-translator":
            from deep_translator import GoogleTranslator
            try:
                return GoogleTranslator(source=source_language, target=target_language).translate(text)
            except Exception as e:
                print("Error in translating concept: ", e)
                raise e
        elif vendor == "googletrans":
            try:
                from googletrans import Translator
            except ImportError:
                raise ImportError("Please install `googletrans` package to use this feature.")
            translator = Translator()
            return translator.translate(text, src=source_language, dest=target_language).text    

        return