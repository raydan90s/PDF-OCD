from app.services.csv_schema import CSV_SCHEMA_DEFAULTS

def normalize_csv_data(llm_data: dict) -> dict:
    final = {}

    for key, default in CSV_SCHEMA_DEFAULTS.items():
        val = llm_data.get(key, default)

        if isinstance(default, int):
            try:
                val = int(val)
            except:
                val = 0

        elif isinstance(default, str):
            if val is None:
                val = ""

        final[key] = val

    return final
