import os
import zipfile
from typing import List


def extract_pdfs_from_zip(zip_path: str, extract_dir: str) -> List[str]:
    pdf_files = []

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    return pdf_files
