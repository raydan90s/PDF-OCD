import requests
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def trigger_n8n(payload: dict):

    file_name = payload.get("file", "desconocido")
    pages = payload.get("pages", 0)

    logger.info(f"Enviando PDF a n8n")
    logger.info(f"Archivo: {file_name}")
    logger.info(f"Páginas: {pages}")

    try:
        response = requests.post(
            settings.N8N_WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        logger.info(f"n8n response status: {response.status_code}")

        response.raise_for_status()

        logger.info(f"PDF enviado correctamente a n8n: {file_name}")

    except requests.exceptions.RequestException:
        logger.exception(f"Error enviando PDF a n8n: {file_name}")
        raise
