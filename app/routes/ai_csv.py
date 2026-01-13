import json
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.services.csv_service import write_single_csv
from app.services.normalizer_service import normalize_csv_data
from app.services.webhook_bd_service import trigger_n8n_subir_bd
from app.utils.generate_csv_filename import generate_csv_filename

router = APIRouter()


async def enviar_a_bd_background(normalized_data: dict, csv_path: str):
    """Envía datos a BD en segundo plano"""
    try:
        payload = {
            "tipo": "ai-csv",
            "csv_path": csv_path,
            "total_registros": 1,
            "data": normalized_data
        }
        trigger_n8n_subir_bd(payload)
    except Exception as e:
        print(f"Error enviando a BD: {e}")


@router.post("/procesar-json-ia")
async def procesar_json_ia(payload: dict, background_tasks: BackgroundTasks):
    try:
        ia_raw = payload.get("data")
        if not ia_raw:
            raise HTTPException(
                status_code=400,
                detail="No se recibió data de la IA"
            )

        if isinstance(ia_raw, str):
            ai_data = json.loads(ia_raw)
        else:
            ai_data = ia_raw

        normalized = normalize_csv_data(ai_data)

        os.makedirs("csv", exist_ok=True)

        csv_name = generate_csv_filename()
        csv_path = f"csv/{csv_name}"

        write_single_csv(normalized, csv_path)

        # Enviar a BD en segundo plano
        if background_tasks:
            background_tasks.add_task(
                enviar_a_bd_background,
                normalized,
                csv_path
            )

        return {
            "status": "ok",
            "csv": csv_path,
            "message": "CSV creado y subiendo a BD"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))