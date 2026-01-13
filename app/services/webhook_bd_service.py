import requests
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

def trigger_n8n_subir_bd(payload: dict):
    """
    Llama al webhook de n8n que sube datos a la base de datos
    """
    try:
        logger.info(f"📤 Enviando datos a BD via n8n")
        
        if not settings.N8N_WEBHOOK_SUBIR_BD:
            logger.warning("⚠️ N8N_WEBHOOK_SUBIR_BD no configurado")
            return None
        
        response = requests.post(
            settings.N8N_WEBHOOK_SUBIR_BD,
            json=payload,
            timeout=60
        )
        
        response.raise_for_status()
        logger.info(f"✅ Datos enviados correctamente a BD")
        return response.json() if response.text else {"status": "ok"}
        
    except requests.exceptions.RequestException as e:
        logger.exception(f"❌ Error enviando datos a BD")
        # No hacemos raise para que no falle el flujo principal
        return None