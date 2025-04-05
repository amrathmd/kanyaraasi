import pytesseract
from PIL import Image
import os

from app.utils.gemini import get_context

current_working_directory = os.getcwd()
async def process_image(document_id, extension):
    # Load image
    img = Image.open(f"{current_working_directory}/{document_id}.{extension}")

    # Extract text
    text = pytesseract.image_to_string(img)

    return get_context(document_id, text)