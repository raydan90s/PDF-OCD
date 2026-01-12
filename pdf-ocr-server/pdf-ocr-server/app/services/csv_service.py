import csv
import os
from app.services.csv_schema import CSV_SCHEMA_DEFAULTS

CSV_HEADERS = list(CSV_SCHEMA_DEFAULTS.keys())


def write_single_csv(data: dict, csv_path: str):
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)
