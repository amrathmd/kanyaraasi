import pytesseract
from PIL import Image
import re


async def process_image(document_id, extension):
    # Load image
    img = Image.open(f"/Users/ajaychitumalla/Desktop/kanyaraasi/Backend/documents/{document_id}.{extension}")

    # Extract text
    text = pytesseract.image_to_string(img)
    print(text)

    # Use regular expression to find the GST Registration No.
    match = re.search(r'GST Registration No:\s*(\S+)', text)

    if match:
        gst_number = match.group(1)  # Extracted GST number
        print("GST Registration Number found:", gst_number)