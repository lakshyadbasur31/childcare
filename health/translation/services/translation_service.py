import hashlib
from django.core.cache import cache
from deep_translator import GoogleTranslator

class TranslationService:
    @staticmethod
    def get_cache_key(text, target_lang):
        # Create a unique key from text and language using MD5 to avoid cache key/length issues
        hashed = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"trans_{target_lang}_{hashed}"

    @classmethod
    def translate(cls, text, target_lang):
        if not text:
            return text
        if not target_lang:
            return text
            
        # Standardize language code to first two characters (e.g. 'kn-IN' -> 'kn')
        target_lang = target_lang.split('-')[0].lower()
        
        # If target language is English, do not translate
        if target_lang == 'en':
            return text
            
        cache_key = cls.get_cache_key(text, target_lang)
        cached_val = cache.get(cache_key)
        if cached_val:
            return cached_val
            
        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            # Handle text length > 4000 chars safely
            if len(text) > 4000:
                chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                translated_chunks = [translator.translate(chunk) for chunk in chunks]
                translated_text = " ".join(translated_chunks)
            else:
                translated_text = translator.translate(text)
                
            # Cache for 24 hours (86400 seconds)
            cache.set(cache_key, translated_text, 86400)
            return translated_text
        except Exception as e:
            # Fallback to original text on translation failure
            print(f"Translation failure in TranslationService: {e}")
            return text
