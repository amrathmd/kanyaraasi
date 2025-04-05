import google.generativeai as genai
import json

def get_context(document_id, text):
    genai.configure(api_key="AIzaSyBIfAJTVkptzaSDVxHPcS6P_eK4-xuNuM8")

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
    print(data)

    # Accessing specific values:
    gstin = data.get("GSTIN")
    total_amount = data.get("Total_Amount")
    cgst_percentage = data.get("CGST_Percentage")
    sgst_percentage = data.get("SGST_Percentage")

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