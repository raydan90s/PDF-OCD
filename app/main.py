from app.utils.logger import get_logger
from app.routes.ai_csv import router as ai_csv_router
from app.routes.client_csv import router as client_csv_router
from app.routes.procesar_archivos import router as procesar_archivos
from fastapi import FastAPI

logger = get_logger(__name__)

app = FastAPI(title="PDF OCR Server")

app.include_router(ai_csv_router)
app.include_router(client_csv_router)
app.include_router(procesar_archivos)