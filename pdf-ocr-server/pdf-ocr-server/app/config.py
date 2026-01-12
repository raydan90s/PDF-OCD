import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_PORT = int(os.getenv("APP_PORT", 3000))
    PDF_RENDER_SCALE = float(os.getenv("PDF_RENDER_SCALE", 2))

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "pdf_ocr")

    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

settings = Settings()
