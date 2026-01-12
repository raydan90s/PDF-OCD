import cloudinary
import cloudinary.uploader
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def upload_image(image_path: str, public_id: str) -> str:
    logger.info(f"Subiendo imagen a Cloudinary: {public_id}")

    try:
        result = cloudinary.uploader.upload(
            image_path,
            folder=settings.CLOUDINARY_FOLDER,
            public_id=public_id,
            resource_type="image"
        )

        url = result["secure_url"]
        logger.info(f"Imagen subida correctamente: {url}")

        return url

    except Exception as e:
        logger.exception(f"Error subiendo imagen {public_id} a Cloudinary")
        raise
