import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.services.client_csv_import_service import adapt_client_csv
from app.services.csv_service import write_single_csv
from app.services.webhook_bd_service import trigger_n8n_subir_bd
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Ruta base del proyecto (igual que en ai_csv.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Sube 3 niveles
CSV_DIR = BASE_DIR / "csv"

# DEBUG: Imprimir rutas al iniciar
logger.info(f"[CLIENT-CSV] BASE_DIR: {BASE_DIR}")
logger.info(f"[CLIENT-CSV] CSV_DIR: {CSV_DIR}")


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
        # Guardar temporal
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Adaptar al schema interno
        normalized_rows = adapt_client_csv(temp_path)
        if not normalized_rows:
            raise HTTPException(status_code=400, detail="CSV sin registros válidos")
        
        # Crear carpeta csv con ruta absoluta
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"[OK] Carpeta CSV cliente creada/verificada: {CSV_DIR}")
        
        # Salida final con ruta absoluta
        output_filename = f"cliente_{file.filename}"
        output_path = CSV_DIR / output_filename
        
        logger.info(f"[SAVE] Guardando CSV cliente en: {output_path}")
        
        # Escribir CSV estándar
        for i, row in enumerate(normalized_rows):
            write_single_csv(row, str(output_path))
        
        # Verificar si el archivo se creó
        if output_path.exists():
            logger.info(f"[SUCCESS] CSV cliente creado: {output_path}")
        else:
            logger.error(f"[ERROR] El CSV cliente NO se creó en: {output_path}")
        
        # Enviar a BD en segundo plano
        if background_tasks:
            background_tasks.add_task(
                enviar_csv_cliente_a_bd_background,
                normalized_rows,
                str(output_path)
            )
        
        return {
            "status": "ok",
            "rows": len(normalized_rows),
            "csv": str(output_path),
            "message": "CSV procesado y subiendo a BD"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))