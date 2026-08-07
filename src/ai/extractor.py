import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract_product_information(text: str):

    prompt = f"""
You are an expert Product Data Extraction Assistant.

Extract product information from the text below.

Return ONLY valid JSON.

If a field is missing, return null.

Fields:
- product_name
- manufacturer
- category
- material
- pressure_rating
- weight
- warranty

Product Text:

{text}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-3.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }