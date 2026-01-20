import requests
import json
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def trigger_n8n(payload: dict):
    """Envía un PDF procesado al webhook de n8n"""
    try:
        logger.info("=" * 80)
        logger.info("📤 ENVIANDO A N8N (PDF INDIVIDUAL)")
        logger.info("=" * 80)
        logger.info(f"🔗 URL: {settings.N8N_WEBHOOK_URL}")
        logger.info(f"📄 Archivo: {payload.get('file', 'unknown')}")
        logger.info(f"📊 Páginas: {payload.get('pages', 0)}")
        logger.info(f"🏷️ Source: {payload.get('source', 'unknown')}")
        logger.info("📦 PAYLOAD COMPLETO:")
        logger.info(json.dumps(payload, indent=2, ensure_ascii=False))
        logger.info("=" * 80)
        
        if not settings.N8N_WEBHOOK_URL:
            logger.warning("⚠️ N8N_WEBHOOK_URL no configurado")
            return None
        
        response = requests.post(
            settings.N8N_WEBHOOK_URL,
            json=payload,
            timeout=30
        )
        
        logger.info(f"✅ Response status: {response.status_code}")
        
        if response.text:
            logger.info(f"📥 Response body: {response.text[:500]}")  # Primeros 500 caracteres
        
        response.raise_for_status()
        logger.info("✅ PDF enviado correctamente a n8n")
        logger.info("=" * 80)
        
        return response.json() if response.text else {"status": "ok"}
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR ENVIANDO A N8N: {e}")
        logger.error("=" * 80)
        return None