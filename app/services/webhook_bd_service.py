import requests
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

def trigger_n8n_subir_bd(payload: dict):
    """
    Llama al webhook de n8n que sube datos a la base de datos
    """
    try:
        logger.info(">> Enviando datos a BD via n8n")
        
        if not settings.N8N_WEBHOOK_SUBIR_BD:
            logger.warning("N8N_WEBHOOK_SUBIR_BD no configurado")
            return None
        
        logger.info(f"URL: {settings.N8N_WEBHOOK_SUBIR_BD}")
        logger.info(f"Tipo: {payload.get('tipo', 'desconocido')}")
        
        response = requests.post(
            settings.N8N_WEBHOOK_SUBIR_BD,
            json=payload,
            timeout=60
        )
        
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        logger.info("Datos enviados correctamente a BD")
        return response.json() if response.text else {"status": "ok"}
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        logger.error(f"Response: {e.response.text if hasattr(e.response, 'text') else 'No response'}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexion: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None