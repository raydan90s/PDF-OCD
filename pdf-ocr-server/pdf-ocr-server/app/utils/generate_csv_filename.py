from datetime import datetime
import uuid


def generate_csv_filename():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    return f"reporte_{ts}_{uid}.csv"
