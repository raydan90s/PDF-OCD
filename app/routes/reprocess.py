import os
from fastapi import APIRouter, HTTPException
from app.services.pdf_processor_service import procesar_pdf_individual
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/reprocesar-pdf")
async def reprocesar_pdf(payload: dict):
    """
    Re-procesa el PDF original usando su UUID.
    Recibe: { "pdf_uuid": "550e8400-e29b-41d4-a716-446655440000" }
    """
    try:
        pdf_uuid = payload.get("pdf_uuid")
        
        if not pdf_uuid:
            raise HTTPException(status_code=400, detail="pdf_uuid es requerido")
        
        # Buscar el PDF en el almacenamiento
        pdf_storage_dir = "uploads/pdfs_originales"
        
        if not os.path.exists(pdf_storage_dir):
            raise HTTPException(status_code=404, detail="Directorio de PDFs no existe")
        
        # Buscar archivo que contenga el UUID
        pdf_file = None
        for file in os.listdir(pdf_storage_dir):
            if file.startswith(pdf_uuid):
                pdf_file = os.path.join(pdf_storage_dir, file)
                break
        
        if not pdf_file:
            raise HTTPException(
                status_code=404,
                detail=f"PDF con UUID {pdf_uuid} no encontrado"
            )
        
        logger.info(f"🔄 Re-procesando PDF: {pdf_file}")
        
        # RE-PROCESAR
        resultado = await procesar_pdf_individual(
            pdf_path=pdf_file,
            original_name=os.path.basename(pdf_file),
            source="reprocess"
        )
        
        return {
            "status": "ok",
            "message": "PDF re-procesado exitosamente",
            "pdf_uuid": pdf_uuid,
            "resultado": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-procesando: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))