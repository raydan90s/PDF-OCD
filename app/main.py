import os
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.config import settings
from app.utils.logger import get_logger

from app.services.pdf_processor_service import procesar_pdf_individual
from app.services.zip_service import extract_pdfs_from_zip

from app.routes.ai_csv import router as ai_csv_router
from app.routes.client_csv import router as client_csv_router

logger = get_logger(__name__)

app = FastAPI(title="PDF OCR Server")

app.include_router(ai_csv_router)
app.include_router(client_csv_router)


@app.post("/procesar-archivos")
async def procesar_archivos(files: List[UploadFile] = File(...)):
    logger.info(f"Archivos recibidos: {len(files)}")

    resultados = []

    for file in files:
        logger.info(f"Procesando archivo: {file.filename}")

        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)

        # Guardar archivo temporal
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # ==========================
        # PDF DIRECTO
        # ==========================
        if file.content_type == "application/pdf":
            resultado = await procesar_pdf_individual(
                pdf_path=file_path,
                original_name=file.filename,
                source="pdf"
            )
            resultados.append(resultado)

        # ==========================
        # ZIP
        # ==========================
        elif file.content_type in [
            "application/zip",
            "application/x-zip-compressed"
        ]:
            pdf_paths = extract_pdfs_from_zip(file_path, temp_dir)

            if not pdf_paths:
                raise HTTPException(
                    status_code=400,
                    detail=f"El ZIP {file.filename} no contiene PDFs"
                )

            for pdf_path in pdf_paths:
                resultado = await procesar_pdf_individual(
                    pdf_path=pdf_path,
                    original_name=os.path.basename(pdf_path),
                    source="zip"
                )
                resultados.append(resultado)

        else:
            logger.error(f"Tipo de archivo no soportado: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} no es PDF ni ZIP"
            )

    return {
        "status": "ok",
        "total_files": len(resultados),
        "files": resultados
    }
