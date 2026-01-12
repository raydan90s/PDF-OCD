import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.client_csv_import_service import adapt_client_csv
from app.services.csv_service import write_single_csv

router = APIRouter()


@router.post("/procesar-csv-cliente")
async def procesar_csv_cliente(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser CSV")

    try:
        # 📂 guardar temporal
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 🔄 adaptar al schema interno
        normalized_rows = adapt_client_csv(temp_path)

        if not normalized_rows:
            raise HTTPException(status_code=400, detail="CSV sin registros válidos")

        # 📁 salida final
        os.makedirs("csv", exist_ok=True)
        output_path = os.path.join("csv", f"cliente_{file.filename}")

        # 🧾 escribir CSV estándar
        for i, row in enumerate(normalized_rows):
            write_single_csv(row, output_path)

        return {
            "status": "ok",
            "rows": len(normalized_rows),
            "csv": output_path
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
