import os
import tempfile
import shutil
import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from app.config import settings
from app.utils.logger import get_logger
from app.services.pdf_processor_service import procesar_pdf_individual
from app.services.zip_service import extract_pdfs_from_zip
from app.services.webhook_bd_service import trigger_n8n_subir_bd
from app.routes.ai_csv import router as ai_csv_router
from app.routes.client_csv import router as client_csv_router

logger = get_logger(__name__)

app = FastAPI(title="PDF OCR Server")
app.include_router(ai_csv_router)
app.include_router(client_csv_router)


async def enviar_pdfs_a_bd_background(resultados: list):
    """Envía resultados de PDFs procesados a BD en segundo plano"""
    try:
        payload = {
            "tipo": "procesar-archivos",
            "total_archivos": len(resultados),
            "archivos": resultados
        }
        trigger_n8n_subir_bd(payload)
    except Exception as e:
        logger.error(f"Error enviando PDFs a BD: {e}")


async def procesar_pdf_seguro(pdf_path: str, original_name: str, source: str):
    """Procesa un PDF con manejo de errores"""
    try:
        resultado = await procesar_pdf_individual(
            pdf_path=pdf_path,
            original_name=original_name,
            source=source
        )
        return resultado
    except Exception as e:
        logger.error(f"❌ Error procesando {original_name}: {e}")
        return {
            "file": original_name,
            "error": str(e),
            "status": "failed",
            "pages": 0,
            "images": []
        }


async def procesar_lote_pdfs(pdf_tasks: List, max_concurrent: int):
    """Procesa PDFs en lotes controlados para evitar saturar memoria"""
    resultados = []
    total_pdfs = len(pdf_tasks)
    
    logger.info(f"🔄 Procesando {total_pdfs} PDFs en lotes de {max_concurrent}")
    
    # Procesar en grupos de MAX_CONCURRENT_PDFS
    for i in range(0, total_pdfs, max_concurrent):
        lote = pdf_tasks[i:i + max_concurrent]
        lote_num = (i // max_concurrent) + 1
        total_lotes = (total_pdfs + max_concurrent - 1) // max_concurrent
        
        logger.info(f"📦 Lote {lote_num}/{total_lotes}: procesando {len(lote)} PDFs")
        
        # Procesar el lote en paralelo
        lote_resultados = await asyncio.gather(*lote, return_exceptions=True)
        
        # Recopilar resultados
        for resultado in lote_resultados:
            if isinstance(resultado, Exception):
                logger.error(f"💥 Excepción en lote: {resultado}")
                resultados.append({
                    "error": str(resultado),
                    "status": "failed"
                })
            else:
                resultados.append(resultado)
        
        logger.info(f"✅ Lote {lote_num}/{total_lotes} completado")
    
    return resultados


@app.post("/procesar-archivos")
async def procesar_archivos(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    # Validar cantidad de archivos
    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Máximo {settings.MAX_FILES_PER_REQUEST} archivos por request. Recibidos: {len(files)}"
        )
    
    logger.info(f"📥 Recibidos {len(files)} archivo(s)")
    
    # Crear directorio temporal ÚNICO
    temp_dir = tempfile.mkdtemp()
    logger.info(f"📁 Dir temporal: {temp_dir}")
    
    pdf_tasks = []
    
    try:
        # ==========================
        # PASO 1: Guardar y preparar archivos
        # ==========================
        for file in files:
            logger.info(f"📄 Archivo: {file.filename} ({file.content_type})")
            file_path = os.path.join(temp_dir, file.filename)
            
            # Guardar archivo
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
                logger.info(f"💾 Guardado: {len(content)} bytes")
            
            # PDF DIRECTO
            if file.content_type == "application/pdf":
                task = procesar_pdf_seguro(
                    pdf_path=file_path,
                    original_name=file.filename,
                    source="pdf"
                )
                pdf_tasks.append(task)
            
            # ZIP
            elif file.content_type in ["application/zip", "application/x-zip-compressed"]:
                logger.info(f"📦 Extrayendo ZIP: {file.filename}")
                
                pdf_paths = extract_pdfs_from_zip(file_path, temp_dir)
                
                if not pdf_paths:
                    raise HTTPException(
                        status_code=400,
                        detail=f"El ZIP {file.filename} no contiene PDFs"
                    )
                
                logger.info(f"✅ {len(pdf_paths)} PDFs extraídos del ZIP")
                
                # Agregar cada PDF a las tareas
                for pdf_path in pdf_paths:
                    task = procesar_pdf_seguro(
                        pdf_path=pdf_path,
                        original_name=os.path.basename(pdf_path),
                        source="zip"
                    )
                    pdf_tasks.append(task)
            
            else:
                logger.error(f"❌ Tipo no soportado: {file.content_type}")
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} debe ser PDF o ZIP"
                )
        
        # ==========================
        # PASO 2: Procesar en lotes
        # ==========================
        if not pdf_tasks:
            raise HTTPException(
                status_code=400,
                detail="No se encontraron PDFs para procesar"
            )
        
        logger.info(f"🚀 Iniciando procesamiento de {len(pdf_tasks)} PDFs")
        
        resultados = await procesar_lote_pdfs(
            pdf_tasks,
            settings.MAX_CONCURRENT_PDFS
        )
        
        # ==========================
        # PASO 3: Enviar a BD
        # ==========================
        if background_tasks:
            background_tasks.add_task(enviar_pdfs_a_bd_background, resultados)
            logger.info("📤 Tarea de envío a BD programada")
        
        # Estadísticas
        exitosos = sum(1 for r in resultados if r.get("status") != "failed")
        fallidos = len(resultados) - exitosos
        
        logger.info(f"✅ Procesamiento completado: {exitosos} exitosos, {fallidos} fallidos")
        
        return {
            "status": "ok",
            "total_files": len(resultados),
            "exitosos": exitosos,
            "fallidos": fallidos,
            "files": resultados,
            "message": "Archivos procesados. Subiendo a BD en segundo plano."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    finally:
        # 🧹 SIEMPRE limpiar archivos temporales
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"🗑️ Limpieza completada: {temp_dir}")
        except Exception as e:
            logger.error(f"⚠️ Error limpiando temp_dir: {e}")


@app.get("/")
async def root():
    return {
        "service": "PDF OCR Server",
        "version": "1.0",
        "max_concurrent_pdfs": settings.MAX_CONCURRENT_PDFS,
        "max_files_per_request": settings.MAX_FILES_PER_REQUEST
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}