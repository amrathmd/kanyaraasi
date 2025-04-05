import google.generativeai as genai
import json
import re

def to_snake_case(key):
    key = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', key)  # insert _ before caps
    return key.lower()

def get_context(document_id, text):
    genai.configure(api_key="AIzaSyBdEdHkb0VOOtoV1X0cRE0M1uV84XebQz4")

    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = ("Identify the GSTIN number, total amount, CGST %, SGST % present in the text and give me JSON. "
              "I need only the required JSON object in string no additional text.")
    augmented_prompt = f"""Please provide context and relevant information from the following text:

    --- TEXT START ---
    {text}
    --- TEXT END ---

    Based on this text, address the following: {prompt}
    """

    response = model.generate_content(augmented_prompt)

    lines = response.text.strip().split('\n')

    if len(lines) > 2:
        # Extract the content between the first and last newline
        middle_content = "\n".join(lines[1:-1])
    elif len(lines) == 2:
        # If only two lines, take the second line
        middle_content = lines[1]
    elif len(lines) == 1:
        # If only one line, that's the middle content
        middle_content = lines[0]
    else:
        middle_content = ""

    data = json.loads(middle_content)
    data  = {to_snake_case(k): v for k, v in data.items()}
    print(data)


    # Accessing specific values:
    gstin = data.get("gstin")
    total_amount = data.get("total_amount")
    cgst_percentage = data.get("cgst_percentage")
    sgst_percentage = data.get("sgst_percentage")

    print(gstin)
    print(total_amount)
    print(cgst_percentage)
    print(sgst_percentage)

    return {
        "gstin": gstin,
        "total": total_amount,
        "cgst": cgst_percentage,
        "sgst": sgst_percentage
    }