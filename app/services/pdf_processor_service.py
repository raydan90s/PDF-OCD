import os
import uuid
import shutil
from app.config import settings
from app.services.pdf_service import pdf_to_images
from app.services.cloudinary_service import upload_image
from app.services.webhook_service import trigger_n8n

async def procesar_pdf_individual(pdf_path: str, original_name: str, source: str = "pdf"):
    # ====================================================
    # 🆕 GUARDAR PDF ORIGINAL ANTES DE PROCESARLO
    # ====================================================
    pdf_storage_dir = "uploads/pdfs_originales"
    os.makedirs(pdf_storage_dir, exist_ok=True)
    
    # Generar nombre único pero rastreable
    pdf_uuid = str(uuid.uuid4())
    stored_pdf_name = f"{pdf_uuid}_{original_name}"
    stored_pdf_path = os.path.join(pdf_storage_dir, stored_pdf_name)
    
    # Copiar PDF a almacenamiento permanente
    shutil.copy2(pdf_path, stored_pdf_path)
    
    # ====================================================
    # Procesamiento normal (tu código actual)
    # ====================================================
    images = pdf_to_images(pdf_path, settings.PDF_RENDER_SCALE)
    uploaded_urls = []
    base_dir = os.path.dirname(pdf_path)

    for page_num, image in images:
        image_name = f"{uuid.uuid4()}_page_{page_num}.png"
        image_path = os.path.join(base_dir, image_name)
        image.save(image_path, "PNG")
        
        url = upload_image(
            image_path=image_path,
            public_id=image_name.replace(".png", "")
        )
        uploaded_urls.append(url)

    # ====================================================
    # 🆕 INCLUIR REFERENCIA AL PDF EN EL PAYLOAD
    # ====================================================
    pdf_payload = {
        "file": original_name,
        "pages": len(uploaded_urls),
        "images": uploaded_urls,
        "source": source,
        "pdf_uuid": pdf_uuid,  # 🆕 Identificador único
        "pdf_stored_path": stored_pdf_path,  # 🆕 Ruta del PDF guardado
        "pdf_stored_name": stored_pdf_name  # 🆕 Nombre del archivo
    }

    trigger_n8n(pdf_payload)
    return pdf_payload