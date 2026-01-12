import json
import os
from fastapi import APIRouter, HTTPException
from app.services.csv_service import write_single_csv
from app.services.normalizer_service import normalize_csv_data
from app.utils.generate_csv_filename import generate_csv_filename

router = APIRouter()

@router.post("/procesar-json-ia")
async def procesar_json_ia(payload: dict):
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

        return {
            "status": "ok",
            "csv": csv_path
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
