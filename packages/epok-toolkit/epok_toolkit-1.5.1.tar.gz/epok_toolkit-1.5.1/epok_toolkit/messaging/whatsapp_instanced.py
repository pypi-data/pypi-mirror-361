from .whatsapp import WhatsappClient
from django.conf import settings
from celery import shared_task



@shared_task
def send_whatsapp_message_async(number: str, message: str):
    from colorstreak import log
    log.debug(f"Enviando mensaje a {number}: '{message}'")
    API_KEY = settings.API_KEY
    INSTANCE = settings.INSTANCE
    SERVER_URL = settings.SERVER_URL

    client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)
    return client.send_text(number, message)

def send_text(number: str, message: str):
    from colorstreak import log
    log.debug(f"Programando tarea para {number}")
    send_whatsapp_message_async.delay(number, message)