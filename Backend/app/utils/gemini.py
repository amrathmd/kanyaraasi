# gemini.py
# Utility functions for interacting with Google's Gemini Generative AI model.

import logging
import json
import re
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions # For specific Google API errors

# Import API key from central settings
from app.core.settings import GEMINI_API_KEY

# Setup logger for this module
logger = logging.getLogger(__name__)

# Configure Gemini API key at module load time
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Google Generative AI (Gemini) configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}. Ensure GEMINI_API_KEY is valid.")
        # Depending on application requirements, might raise an error or allow graceful degradation.
else:
    logger.warning("GEMINI_API_KEY not found in settings. Gemini functionality will be disabled.")


class GeminiError(Exception):
    """Custom exception for errors related to Gemini API interaction."""
    pass


def to_snake_case(key: str) -> str:
    """Converts a string to snake_case."""
    if not key: # Handle empty string case
        return ""
    key = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', key)  # Insert _ before caps following a lowercase/digit
    key = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', '_', key) # Insert _ before caps if it's part of a sequence like "HTTPRequest" -> "HTTP_Request"
    return key.lower()


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to extract a JSON object from the LLM's response text.
    Handles cases where JSON might be embedded within markdown code blocks (```json ... ```)
    or as a plain string.
    """
    if not response_text:
        return None

    # Try to find JSON within markdown code blocks
    match = re.search(r"```json\s*([\s\S]*?)\s*```", response_text, re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from markdown block: {e}. Content: '{json_str[:200]}...'")
            # Fall through to try parsing the whole text or other methods

    # Try parsing the whole text if no markdown block found or if parsing failed
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        # The original line-splitting logic as a fallback, though it's brittle.
        # This part might need significant improvement or removal if LLM output is inconsistent.
        lines = response_text.strip().split('\n')
        middle_content = ""
        if len(lines) > 2 and lines[0].strip().startswith("```") and lines[-1].strip().startswith("```"):
            middle_content = "\n".join(lines[1:-1]) # Assumes ```json ... ``` without 'json' tag
        elif len(lines) == 1: # If only one line, assume it's the JSON
             middle_content = lines[0]
        # Add more sophisticated extraction if needed

        if middle_content:
            try:
                return json.loads(middle_content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from extracted middle_content: {e}. Content: '{middle_content[:200]}...'")
                return None
        else:
            logger.error(f"Could not extract valid JSON from Gemini response. Raw response: '{response_text[:500]}...'")
            return None


def get_extracted_invoice_data(document_id: str, text: str) -> Dict[str, Any]:
    """
    Uses Gemini to extract structured data (GSTIN, total amount, CGST, SGST)
    from unstructured text content of a document.

    Args:
        document_id: Identifier for the document (used for logging/context if needed by Gemini).
        text: The raw text extracted from the document by OCR.

    Returns:
        A dictionary containing the extracted fields:
        {
            "gstin": Optional[str],
            "total_amount": Optional[Any],  // Type depends on LLM output, ideally float/Decimal
            "cgst_percentage": Optional[Any], // Type depends on LLM output
            "sgst_percentage": Optional[Any]  // Type depends on LLM output
        }
        Values can be None if not found or if an error occurs.

    Raises:
        GeminiError: If the Gemini API key is not configured or if API interaction fails.
    """
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not configured. Cannot process text.")
        raise GeminiError("Gemini API key is not configured.")

    try:
        # Model selection can be made configurable if needed
        model = genai.GenerativeModel('gemini-1.5-pro') # Or 'gemini-pro' for potentially faster/cheaper
        logger.debug(f"Using Gemini model: {model.model_name} for document ID: {document_id}")

        # Refined prompt for better JSON output and clarity
        prompt_instructions = (
            "From the provided text, identify the following details: "
            "GSTIN (Goods and Services Tax Identification Number), "
            "total invoice amount (as a number), "
            "CGST percentage (Central Goods and Services Tax, as a number, e.g., 9 for 9%), and "
            "SGST percentage (State Goods and Services Tax, as a number, e.g., 9 for 9%).\n"
            "Return these details STRICTLY as a single JSON object. Do not include any explanatory text, "
            "markdown formatting for the JSON block, or any other content outside the JSON object itself. "
            "If a value is not found, use null for that key in the JSON. "
            "Example JSON format: "
            '{"gstin": "YOUR_GSTIN", "total_amount": 1234.50, "cgst_percentage": 9, "sgst_percentage": 9}'
        )

        # Using a more structured prompt format if supported by the SDK, or just f-string
        augmented_prompt = f"""Context: You are an AI assistant extracting information from an invoice.
        Document Text:
        --- TEXT START ---
        {text}
        --- TEXT END ---

        Task: {prompt_instructions}
        """

        logger.debug(f"Sending augmented prompt to Gemini for document ID: {document_id}")
        response = model.generate_content(augmented_prompt)
        logger.debug(f"Received response from Gemini for document ID {document_id}. Raw text length: {len(response.text)}")

        extracted_data_dict = extract_json_from_response(response.text)

        if not extracted_data_dict:
            logger.error(f"Failed to extract valid JSON data from Gemini response for document ID {document_id}.")
            # Fallback to returning None for all fields if JSON parsing fails completely
            return {
                "gstin": None, "total_amount": None,
                "cgst_percentage": None, "sgst_percentage": None
            }

        # Convert keys to snake_case for consistency
        snake_case_data = {to_snake_case(k): v for k, v in extracted_data_dict.items()}
        logger.info(f"Processed data from Gemini for doc_id {document_id}: {snake_case_data}")

        # Ensure specific keys are present, defaulting to None if missing after snake_case conversion
        # The OCR processing logic in documents.py expects "total", "cgst", "sgst"
        # This function will return "total_amount", "cgst_percentage", "sgst_percentage"
        # The caller (OCR task) needs to map these names or this function should return the expected names.
        # For now, returning the snake_cased names from LLM.
        # Caller needs to be aware of potential type issues (e.g. amount as string vs float)
        return {
            "gstin": snake_case_data.get("gstin"),
            "total_amount": snake_case_data.get("total_amount"), # Caller should convert to Decimal
            "cgst_percentage": snake_case_data.get("cgst_percentage"), # Caller should convert to Decimal/float
            "sgst_percentage": snake_case_data.get("sgst_percentage")  # Caller should convert to Decimal/float
        }

    except google_exceptions.GoogleAPIError as e:
        logger.error(f"Gemini API error for document ID {document_id}: {e}")
        raise GeminiError(f"Gemini API interaction failed: {e}")
    except json.JSONDecodeError as e: # Should be caught by extract_json_from_response, but as safeguard
        logger.error(f"JSON decoding error from Gemini response for document ID {document_id}: {e}")
        raise GeminiError(f"Failed to decode JSON from Gemini response: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Gemini processing for document ID {document_id}: {e}")
        raise GeminiError(f"An unexpected error occurred with Gemini: {e}")

# Original function name get_context, renamed to get_extracted_invoice_data for clarity.
# The return keys were also changed to be more descriptive (e.g. "total" -> "total_amount").
# The OCR processing logic in run_ocr_processing_task will need to be updated to use these new keys.