from health.translation.services.translation_service import TranslationService
import time

class SMSService:
    """
    Mock SMS Service for sending translated alerts to users.
    """
    
    @classmethod
    def send_alert(cls, user, message):
        """
        Translates the given message into the user's preferred language and 'sends' it via SMS.
        """
        if not user.phone_number:
            return False
            
        target_lang = user.preferred_language
        
        # Translate the message if the user's language is not English
        if target_lang != 'en':
            try:
                translated_message = TranslationService.translate(message, target_lang)
            except Exception as e:
                print(f"[SMS SERVICE] Error translating message: {e}")
                translated_message = message
        else:
            translated_message = message
            
        # Simulate Network Delay
        time.sleep(0.5)
        
        # Print brightly colored mock output to terminal
        print("\n" + "="*50)
        print("📱 🚨 MOCK SMS DISPATCHED 🚨 📱")
        print("="*50)
        print(f"To: {user.username} ({user.phone_number})")
        print(f"Language: {target_lang.upper()}")
        print("-" * 50)
        print(translated_message)
        print("="*50 + "\n")
        
        return True
