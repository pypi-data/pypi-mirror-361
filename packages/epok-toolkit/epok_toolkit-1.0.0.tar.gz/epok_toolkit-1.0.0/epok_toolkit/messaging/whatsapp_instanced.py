from .whatsapp import WhatsappClient
from django.conf import settings
from celery import shared_task


API_KEY = settings.API_KEY
INSTANCE = settings.INSTANCE
SERVER_URL = settings.SERVER_URL

client = WhatsappClient(api_key=API_KEY, server_url=SERVER_URL, instance_name=INSTANCE)

@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,       # 2, 4, 8, 16… s
    retry_jitter=True,        # +- aleatorio
    max_retries=3,
    ignore_result=True,       # <-- ¡importante!
)
def send_whatsapp_message(number: str, message: str):
    return client.send_text(number, message)

