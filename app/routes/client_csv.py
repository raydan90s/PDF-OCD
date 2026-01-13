import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.services.client_csv_import_service import adapt_client_csv
from app.services.csv_service import write_single_csv
from app.services.webhook_bd_service import trigger_n8n_subir_bd
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def enviar_csv_cliente_a_bd_background(normalized_rows: list, output_path: str):
    """Envía CSV de cliente a BD en segundo plano"""
    try:
        payload = {
            "tipo": "csv-cliente",
            "csv_path": output_path,
            "total_registros": len(normalized_rows),
            "data": normalized_rows
        }
        trigger_n8n_subir_bd(payload)
    except Exception as e:
        logger.error(f"Error enviando CSV cliente a BD: {e}")


@router.post("/procesar-csv-cliente")
async def procesar_csv_cliente(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser CSV")
    
    try:
        # 📂 guardar temporal
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # 📄 adaptar al schema interno
        normalized_rows = adapt_client_csv(temp_path)
        if not normalized_rows:
            raise HTTPException(status_code=400, detail="CSV sin registros válidos")
        
        # 📁 salida final
        os.makedirs("csv", exist_ok=True)
        output_path = os.path.join("csv", f"cliente_{file.filename}")
        
        # 🧾 escribir CSV estándar
        for i, row in enumerate(normalized_rows):
            write_single_csv(row, output_path)
        
        # ✨ NUEVO: Enviar a BD en segundo plano
        if background_tasks:
            background_tasks.add_task(
                enviar_csv_cliente_a_bd_background,
                normalized_rows,
                output_path
            )
        
        return {
            "status": "ok",
            "rows": len(normalized_rows),
            "csv": output_path,
            "message": "CSV procesado y subiendo a BD"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))