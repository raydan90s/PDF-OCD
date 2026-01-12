import pypdfium2 as pdfium
from app.utils.logger import get_logger

logger = get_logger(__name__)


def pdf_to_images(pdf_path: str, scale: float):
    logger.info(f"Abriendo PDF: {pdf_path}")
    logger.info(f"Escala de renderizado: {scale}")

    pdf = pdfium.PdfDocument(pdf_path)
    images = []

    total_pages = len(pdf)
    logger.info(f"Total de páginas detectadas: {total_pages}")

    for index, page in enumerate(pdf):
        page_number = index + 1
        logger.info(f"Renderizando página {page_number}/{total_pages}")

        img = page.render(scale=scale).to_pil()
        images.append((page_number, img))

    logger.info(f"Renderizado completo ({len(images)} imágenes)")

    return images
