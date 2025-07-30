from .whatsapp import WhatsappClient
from django.conf import settings
from celery import shared_task


API_KEY = settings.API_KEY
INSTANCE = settings.INSTANCE
SERVER_URL = settings.SERVER_URL

@shared_task
def send_whatsapp_message_async(number: str, message: str):
    try:
        from colorstreak import log
        log.debug(f"Enviando mensaje a {number}: '{message}'")

        client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)
        return client.send_text(number, message)
    except Exception as e:
        log.error(f"Error al enviar mensaje a {number}: {e}")

def send_text(number: str, message: str):
    from colorstreak import log
    log.debug(f"Programando tarea para {number}")
    send_whatsapp_message_async.delay(number, message)