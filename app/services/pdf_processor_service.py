import os
import uuid
from app.config import settings
from app.services.pdf_service import pdf_to_images
from app.services.cloudinary_service import upload_image
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def procesar_pdf_individual(pdf_path: str, original_name: str, source: str = "pdf"):
    """Procesa un PDF: convierte a imágenes y sube a Cloudinary"""
    
    logger.info(f"🔄 Procesando: {original_name}")
    
    try:
        # Convertir PDF a imágenes
        images = pdf_to_images(pdf_path, settings.PDF_RENDER_SCALE)
        
        if not images:
            raise ValueError(f"No se pudieron extraer imágenes de {original_name}")
        
        uploaded_urls = []
        base_dir = os.path.dirname(pdf_path)

        # Procesar cada página
        for page_num, image in images:
            image_name = f"{uuid.uuid4()}_page_{page_num}.png"
            image_path = os.path.join(base_dir, image_name)

            try:
                # Guardar imagen temporal
                image.save(image_path, "PNG")
                logger.info(f"  📄 Página {page_num} guardada")

                # Subir a Cloudinary
                url = upload_image(
                    image_path=image_path,
                    public_id=image_name.replace(".png", "")
                )
                uploaded_urls.append(url)
                logger.info(f"  ☁️ Página {page_num} subida a Cloudinary")

            finally:
                # Limpiar imagen temporal inmediatamente
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar {image_path}: {e}")

        # Resultado final
        pdf_payload = {
            "file": original_name,
            "pages": len(uploaded_urls),
            "images": uploaded_urls,
            "source": source,
            "status": "success"
        }

        logger.info(f"✅ {original_name}: {len(uploaded_urls)} páginas procesadas")
        
        # ❌ NO enviar individualmente a n8n
        # trigger_n8n(pdf_payload)  # <-- COMENTADO

        return pdf_payload
    
    except Exception as e:
        logger.error(f"❌ Error en {original_name}: {e}")
        raise Exception(f"Error procesando {original_name}: {str(e)}")