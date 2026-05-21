import logging
import time
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Thread pool for asynchronous SMS dispatch
sms_executor = ThreadPoolExecutor(max_workers=3)

class BaseSMSProvider(ABC):
    @abstractmethod
    def send_sms(self, phone_number, message):
        """
        Send SMS to the specified phone number.
        Must return True if successful, False otherwise.
        """
        pass

class ConsoleSMSProvider(BaseSMSProvider):
    def send_sms(self, phone_number, message):
        print(f"\n[SMS OUTBOX] TO: {phone_number} | MESSAGE: {message}\n")
        logger.info(f"SMS sent successfully to {phone_number}")
        return True

# Instantiate default provider
default_sms_provider = ConsoleSMSProvider()

def dispatch_sms_async(phone_number, message, provider=None, max_retries=3, backoff_factor=2):
    """
    Submit SMS sending task to the background thread pool with retry logic and exponential backoff.
    """
    if not phone_number:
        logger.warning("SMS dispatch requested but phone number is empty.")
        return
        
    if provider is None:
        provider = default_sms_provider
        
    def worker():
        retries = 0
        delay = 1.0
        while retries < max_retries:
            try:
                success = provider.send_sms(phone_number, message)
                if success:
                    return
            except Exception as e:
                logger.error(f"Error sending SMS on attempt {retries + 1}: {e}")
            retries += 1
            if retries < max_retries:
                time.sleep(delay)
                delay *= backoff_factor
        logger.error(f"Failed to send SMS to {phone_number} after {max_retries} attempts.")

    sms_executor.submit(worker)
