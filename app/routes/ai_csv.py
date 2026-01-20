async def enviar_a_bd_background(normalized_data: list, csv_path: str, pdf_uuid: str = None):
    """Envía datos a BD en segundo plano"""
    try:
        payload = {
            "tipo": "ai-csv",
            "csv_path": csv_path,
            "pdf_uuid": pdf_uuid,  # 🆕 Incluir UUID del PDF
            "total_registros": len(normalized_data),
            "data": normalized_data
        }
        trigger_n8n_subir_bd(payload)
    except Exception as e:
        logger.error(f"Error enviando a BD: {e}")

@router.post("/procesar-json-ia")
async def procesar_json_ia(payload: dict, background_tasks: BackgroundTasks):
    try:
        ia_raw = payload.get("data")
        pdf_uuid = payload.get("pdf_uuid")  # 🆕 Recibir UUID
        
        if not ia_raw:
            raise HTTPException(status_code=400, detail="No se recibió data de la IA")
        
        if isinstance(ia_raw, str):
            ai_data = json.loads(ia_raw)
        else:
            ai_data = ia_raw
        
        normalized = normalize_csv_data(ai_data)
        
        os.makedirs("csv", exist_ok=True)
        csv_name = generate_csv_filename()
        csv_path = f"csv/{csv_name}"
        write_single_csv(normalized, csv_path)
        
        # 🆕 Pasar pdf_uuid al background task
        background_tasks.add_task(
            enviar_a_bd_background,
            normalized,
            csv_path,
            pdf_uuid
        )
        
        return {
            "status": "ok",
            "csv": csv_path,
            "pdf_uuid": pdf_uuid,
            "message": "CSV creado y subiendo a BD"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))