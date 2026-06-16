import os
import requests
from runtime.logger import logger
from config import settings

def send_telegram_notification(message: str) -> bool:
    """
    Envía un mensaje formateado a un bot de Telegram si las credenciales 
    están configuradas en config/settings o en las variables de entorno.
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", os.getenv("TELEGRAM_CHAT_ID", ""))
    
    if not token or not chat_id:
        return False
        
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        # Timeout corto de 4 segundos para evitar bloquear el runtime de la agencia
        response = requests.post(url, json=payload, timeout=4)
        response.raise_for_status()
        logger.info("[TELEGRAM] Notificación de error enviada exitosamente al chat administrador.")
        return True
    except Exception as e:
        logger.warning(f"[TELEGRAM] No se pudo enviar la notificación de error: {str(e)}")
        return False
