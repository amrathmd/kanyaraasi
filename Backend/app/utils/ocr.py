import pytesseract
from PIL import Image

from app.utils.gemini import get_context


async def process_image(document_id, extension):
    # Load image
    img = Image.open(f"/Users/ajaychitumalla/Desktop/kanyaraasi/Backend/documents/{document_id}.{extension}")

    # Extract text
    text = pytesseract.image_to_string(img)

    return get_context(document_id, text)