import requests
import json
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def trigger_n8n_subir_bd(payload: dict):
    """
    Llama al webhook de n8n que sube datos a la base de datos
    """
    try:
        logger.info("=" * 80)
        logger.info("📤 ENVIANDO A N8N (BD)")
        logger.info("=" * 80)
        logger.info(f"🔗 URL: {settings.N8N_WEBHOOK_SUBIR_BD}")
        logger.info(f"🏷️ Tipo: {payload.get('tipo', 'desconocido')}")
        
        if payload.get('tipo') == 'ai-csv':
            logger.info(f"📊 Total registros: {payload.get('total_registros', 0)}")
            logger.info(f"📁 CSV path: {payload.get('csv_path', 'N/A')}")
            logger.info(f"📋 Registros en data: {len(payload.get('data', []))}")
            
            # Mostrar primer registro como ejemplo
            if payload.get('data'):
                try:
                    data = payload['data']
                    if isinstance(data, list) and len(data) > 0:
                        logger.info("📄 EJEMPLO - Primer registro:")
                        logger.info(json.dumps(data[0], indent=2, ensure_ascii=False))
                    elif isinstance(data, dict):
                        logger.info("📄 EJEMPLO - Datos:")
                        logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                except (IndexError, KeyError, TypeError) as e:
                    logger.warning(f"No se pudo mostrar ejemplo de datos: {e}")
        
        elif payload.get('tipo') == 'procesar-archivos':
            logger.info(f"📊 Total archivos: {payload.get('total_archivos', 0)}")
            logger.info(f"📋 Archivos procesados: {len(payload.get('archivos', []))}")
        
        logger.info("📦 PAYLOAD COMPLETO:")
        logger.info(json.dumps(payload, indent=2, ensure_ascii=False))
        logger.info("=" * 80)
        
        if not settings.N8N_WEBHOOK_SUBIR_BD:
            logger.warning("⚠️ N8N_WEBHOOK_SUBIR_BD no configurado")
            return None
        
        response = requests.post(
            settings.N8N_WEBHOOK_SUBIR_BD,
            json=payload,
            timeout=60
        )
        
        logger.info(f"✅ Response status: {response.status_code}")
        
        if response.text:
            logger.info(f"📥 Response body: {response.text[:500]}")
        
        response.raise_for_status()
        logger.info("✅ Datos enviados correctamente a n8n BD")
        logger.info("=" * 80)
        
        return response.json() if response.text else {"status": "ok"}
        
    except requests.exceptions.HTTPError as e:
        logger.error("=" * 80)
        logger.error(f"❌ HTTP Error: {e}")
        logger.error(f"📥 Response: {e.response.text if hasattr(e.response, 'text') else 'No response'}")
        logger.error("=" * 80)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("=" * 80)
        logger.error(f"❌ Error de conexión: {e}")
        logger.error("=" * 80)
        return None
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ Error inesperado: {e}")
        logger.error("=" * 80)
        return None