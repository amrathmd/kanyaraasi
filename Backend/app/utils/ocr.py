# ocr.py
# Utility functions for Optical Character Recognition (OCR) using Tesseract.

import logging
import os # Keep for os.path.exists if needed, but file path now comes as arg
from typing import Any, Dict # For return type of get_context

import pytesseract
from PIL import Image, UnidentifiedImageError # For opening images and handling errors
from fastapi.concurrency import run_in_threadpool # To run blocking IO/CPU tasks

from app.utils.gemini import get_context # Assuming get_context is defined and potentially blocking

# Setup logger for this module
logger = logging.getLogger(__name__)

# current_working_directory = os.getcwd() # No longer needed at module level

class OCRError(Exception):
    """Custom exception for OCR processing errors."""
    pass

async def process_image_with_ocr(file_path: str, document_id_for_context: str) -> Dict[str, Any]:
    """
    Processes an image file using Tesseract OCR to extract text,
    and then sends the extracted text to a context processing function (Gemini).

    Args:
        file_path: The absolute path to the image file to be processed.
        document_id_for_context: The document ID passed to the context processing function.
                                 Its specific use by `get_context` should be understood.

    Returns:
        A dictionary containing the result from the `get_context` function.

    Raises:
        OCRError: If the image cannot be opened, OCR fails, or context processing fails.
    """
    logger.info(f"Starting OCR processing for image at path: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"OCR Error: Image file not found at {file_path}")
        raise OCRError(f"Image file not found: {file_path}")

    try:
        # --- Step 1: Load Image (Blocking I/O) ---
        def _load_image():
            logger.debug(f"Loading image: {file_path}")
            return Image.open(file_path)

        img = await run_in_threadpool(_load_image)
        logger.info(f"Successfully loaded image: {file_path}")

    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        logger.error(f"OCR Error: Image file not found (post-check) at {file_path}")
        raise OCRError(f"Image file not found: {file_path}")
    except UnidentifiedImageError:
        logger.error(f"OCR Error: Cannot identify image file or unsupported format at {file_path}")
        raise OCRError(f"Cannot identify image file (unsupported format?): {file_path}")
    except Exception as e:
        logger.error(f"OCR Error: Unexpected error opening image {file_path}: {e}")
        raise OCRError(f"Unexpected error opening image {file_path}: {e}")

    try:
        # --- Step 2: Extract Text using Tesseract (CPU-bound) ---
        def _extract_text():
            logger.debug(f"Extracting text from image: {file_path} using Tesseract.")
            # Add language if specific, e.g., text = pytesseract.image_to_string(img, lang='eng')
            return pytesseract.image_to_string(img)

        extracted_text = await run_in_threadpool(_extract_text)
        logger.info(f"Successfully extracted text from image: {file_path}. Text length: {len(extracted_text)}")
        if not extracted_text.strip():
            logger.warning(f"OCR for {file_path} resulted in empty or whitespace-only text.")
            # Depending on requirements, this might be an error or just an empty result.
            # For now, proceed with empty text to get_context.

    except pytesseract.TesseractNotFoundError:
        logger.error("OCR Error: Tesseract is not installed or not found in your PATH.")
        raise OCRError("Tesseract OCR engine not found. Please ensure it is installed and in PATH.")
    except Exception as e: # Catch other Tesseract errors
        logger.error(f"OCR Error: Tesseract failed for {file_path}: {e}")
        raise OCRError(f"Tesseract OCR processing failed for {file_path}: {e}")
    finally:
        img.close() # Ensure image is closed

    try:
        # --- Step 3: Process with Gemini (Potentially Blocking I/O or CPU-bound) ---
        # Assuming get_context might be blocking. If it's already async and non-blocking,
        # then `await get_context(...)` would be fine directly.
        def _get_context_sync():
            logger.debug(f"Sending extracted text (doc_id: {document_id_for_context}) to Gemini for context processing.")
            return get_context(document_id_for_context, extracted_text)

        # If get_context is an async function:
        # context_result = await get_context(document_id_for_context, extracted_text)
        # Else, if it's sync/blocking:
        context_result = await run_in_threadpool(_get_context_sync)

        logger.info(f"Successfully processed text with Gemini for doc_id: {document_id_for_context}")
        return context_result

    except Exception as e:
        logger.error(f"Error during Gemini context processing for doc_id {document_id_for_context}: {e}")
        raise OCRError(f"Context processing failed for doc_id {document_id_for_context}: {e}")

# Original function name was process_image. Renamed to process_image_with_ocr for clarity.
# The caller in documents.py was:
# response = asyncio.run(process_image(document_id, extension)) -> This was incorrect if documents.py endpoint was async.
# It should have been `await process_image(...)` if process_image was truly async and non-blocking,
# or wrapped in run_in_threadpool if process_image was sync.
# The new structure with BackgroundTasks and run_in_threadpool inside process_image_with_ocr is more robust.