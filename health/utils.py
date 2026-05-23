import requests
import logging
from health.translation.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

def send_tinycare_whatsapp_alert(parent_phone, child_name, vaccine_name, health_consequence, target_lang='en'):
    """
    Sends a WhatsApp alert via the isolated Node.js gateway.
    
    Args:
        parent_phone (str): The parent's phone number.
        child_name (str): The name of the child.
        vaccine_name (str): The name of the vaccine.
        health_consequence (str): Clinical risk of missing the vaccine.
        
    Returns:
        dict: The JSON response from the gateway, or None if it failed.
    """
    message_text = (
        "🚨 *TinyCare Health Advisory* 🚨\n"
        f"Dear Parent, your hero *{child_name}* is due for the *{vaccine_name}* milestone dose.\n"
        f"⚠️ *Clinical Risk:* {health_consequence}"
    )

    if target_lang != 'en':
        message_text = TranslationService.translate(message_text, target_lang)

    payload = {
        "phone": parent_phone,
        "message": message_text
    }
    
    gateway_url = "http://127.0.0.1:3000/dispatch-message/"
    
    try:
        response = requests.post(gateway_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to send WhatsApp alert for {child_name} to {parent_phone}: {str(e)}")
        return None

def send_tinycare_maternal_whatsapp_alert(parent_phone, mother_name, vital_issue, doctor_recommendation, target_lang='en'):
    """
    Sends a maternal health WhatsApp alert via the isolated Node.js gateway.
    """
    message_text = (
        "🚨 *TinyCare Maternal Alert* 🚨\n"
        f"Dear {mother_name}, we detected a potential issue in your recent recovery logs.\n"
        f"⚠️ *Vital Issue:* {vital_issue}\n"
        f"⚕️ *Recommendation:* {doctor_recommendation}"
    )

    if target_lang != 'en':
        message_text = TranslationService.translate(message_text, target_lang)

    payload = {
        "phone": parent_phone,
        "message": message_text
    }
    
    gateway_url = "http://127.0.0.1:3000/dispatch-message/"
    
    try:
        response = requests.post(gateway_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to send Maternal WhatsApp alert to {parent_phone}: {str(e)}")
        return None

