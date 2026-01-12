import csv
from datetime import datetime
from typing import List

from app.services.csv_schema import CSV_SCHEMA_DEFAULTS
from app.services.normalizer_service import normalize_csv_data


def now_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def normalize_timestamp(value: str) -> str:
    if not value:
        return now_str()

    value = value.strip()

    # Si ya viene en formato DD/MM/YYYY
    if "/" in value:
        return value

    # Intentar ISO u otros formatos
    try:
        dt = datetime.fromisoformat(value.replace("Z", ""))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return now_str()


CLIENT_TO_INTERNAL_MAP = {
    "Nombre del modelo": "modelo_impresora",
    "Dirección IP": "direccion_ip",
    "Nombre del host": "nombre_host",
    "ID de la cuenta": "id_cuenta",
    "Nombre de cuenta": "nombre_cuenta",

    "Imprimir (total)": "total_impresiones",
    "Copia (total)": "total_copias",
    "Escanear (total)": "total_escaneos",

    "Imprimir (a todo color)": "impresion_color",
    "Imprimir (blanco y negro)": "impresion_bn",

    "Copia (a todo color)": "copia_color",
    "Copia (blanco y negro)": "copia_bn",

    "Escanear (copia)": "escaneo_copia",
    "Escanear (FAX)": "escaneo_fax",
    "Escanear (en otro)": "escaneo_otros",

    "Medio 1": "papel_a4",
    "Medio 2": "papel_a5",
}


def adapt_client_csv(file_path: str) -> List[dict]:
    rows = []

    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            internal = dict(CSV_SCHEMA_DEFAULTS)

            # ✅ Fecha desde "Marca de tiempo"
            internal["fecha_registro"] = normalize_timestamp(
                row.get("Marca de tiempo")
            )

            for client_col, internal_key in CLIENT_TO_INTERNAL_MAP.items():
                val = row.get(client_col, "")
                internal[internal_key] = val

            normalized = normalize_csv_data(internal)
            rows.append(normalized)

    return rows
