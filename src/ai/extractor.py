import json
import os
import re

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract_product_information(text: str):

    prompt = f"""
You are an expert Product Data Extraction Assistant for VeritasIQ.

Your task is to extract product information from the provided product document.

Return ONLY valid JSON.

IMPORTANT EXTRACTION RULES:

1. Extract information only when it is explicitly supported by the
   provided document.

2. Do NOT infer, assume, or invent information.

3. If a field is not explicitly stated in the document, return null.

4. Brand and manufacturer are different fields.
   Do not assume that the brand is the manufacturer unless the document
   explicitly identifies the manufacturer.

5. Product type, category, and subcategory are different fields.
   Do not infer a category or subcategory from the product type.
   Only populate category or subcategory when explicitly stated.

6. Preserve the meaning of the source information.

7. Do not convert or normalize values yet.
   Preserve the original extracted meaning. Normalization will be
   performed by a separate VeritasIQ processing layer.

8. Lists such as colors, certifications, and included_items should
   be returned as JSON arrays.

9. Category-specific attributes should be placed inside
   category_specific rather than being added to the universal fields.

10. Do not add category-specific fields to the universal schema.

Required JSON structure:

{{
    "product_name": null,
    "brand": null,
    "manufacturer": null,
    "model_number": null,
    "product_code": null,

    "product_type": null,
    "category": null,
    "subcategory": null,

    "country_of_origin": null,
    "intended_use": null,

    "dimensions": {{
        "length": null,
        "width": null,
        "height": null,
        "unit": null
    }},

    "weight": {{
        "value": null,
        "unit": null
    }},

    "material": null,
    "color": [],
    "size": null,

    "price": {{
        "value": null,
        "currency": null
    }},

    "warranty": {{
        "duration": null,
        "type": null,
        "coverage": null,
        "exclusions": [],
        "provider": null
    }},

    "certifications": [],
    "included_items": [],

    "category_specific": {{}}
}}

CATEGORY-SPECIFIC INFORMATION:

First use explicitly stated product information to identify the
product type/category when available.

Then place important category-specific specifications inside
category_specific.

For example, a smartphone document may contain:

- display
- processor
- RAM
- storage
- battery
- camera
- operating_system
- connectivity
- security
- water_resistance
- audio
- AI_features

A plumbing document may contain:

- pressure_rating
- flow_rate
- connection_size
- valve_type
- installation_type
- operating_temperature

A furniture document may contain:

- load_capacity
- seat_height
- upholstery
- armrest_type
- backrest_type
- adjustability

These are examples only.

Extract category-specific attributes based on what is actually
present in the provided document.

Do not force information into these examples if the source uses
different specifications.

Product Text:

{text}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-3.5-flash",
            contents=prompt,
        )

        raw_response = response.text.strip()

         # Remove Markdown code fences if Gemini returns JSON inside ```json ... ```
        raw_response = re.sub(r"^```json\s*", "", raw_response)
        raw_response = re.sub(r"\s*```$", "", raw_response)

        return json.loads(raw_response)

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }