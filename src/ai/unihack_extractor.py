import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


def extract_unihack_product(
    mfg_part_num: str,
    part_desc: str,
    part_manuf: str | None = None,
):
    """
    Enrich a UniHack catalogue row using web-grounded Gemini extraction.

    The model is instructed to:
    - identify the exact product using the MPN
    - prioritize manufacturer/official sources
    - extract only source-supported information
    - distinguish product identifiers correctly
    - return structured attributes
    - preserve evidence URLs
    - avoid inventing missing information
    """

    manufacturer_context = part_manuf or "Unknown"

    prompt = f"""
You are a product-data enrichment engine for VeritasIQ.

Identify and enrich this exact catalogue product using web search.

PRODUCT INPUT
--------------
Manufacturer/Source field: {manufacturer_context}
Manufacturer Part Number: {mfg_part_num}
Part Description: {part_desc}

OBJECTIVE
---------
Find the exact product corresponding to the manufacturer part number.

Prioritize:
1. Official manufacturer product pages
2. Official manufacturer specification pages
3. Official manufacturer manuals/specification PDFs
4. Other authoritative sources only when an official source cannot provide
   the required information

Do NOT use marketplace listings as the primary evidence when an official
manufacturer source is available.

CRITICAL RULES
--------------
1. Do not invent product information.
2. Do not guess when multiple products could match the MPN.
3. The MPN must correspond to the exact product being described.
4. Manufacturer and brand are separate fields.
5. Preserve source-supported values.
6. Include the URL supporting each important piece of information when
   possible.
7. If a field cannot be verified, return null.
8. Extract category-specific specifications dynamically.
9. Do not fabricate UPC, GTIN, SKU, dimensions, warranty, certifications,
   images, or specifications.
10. Return ONLY valid JSON.

IDENTIFIER RULES
----------------
11. model_number means the manufacturer/model identifier for the exact
    product when explicitly identified by the source.
12. product_code means a product/catalog/item code only when the source
    explicitly identifies the value as a product/catalog/item code.
13. UPC means the Universal Product Code. Never place a UPC in
    model_number or product_code.
14. EAN means the European Article Number. Never place an EAN in
    model_number or product_code.
15. GTIN means the Global Trade Item Number. Never place a GTIN in
    model_number or product_code.
16. SKU means a seller/distributor stock keeping unit. Do not treat a SKU
    as a manufacturer part number unless the source explicitly identifies
    it as such.
17. If an identifier cannot be verified, return null.
18. The input manufacturer part number may contain a distributor prefix
    or formatting. Resolve the actual manufacturer identifier only when
    authoritative evidence supports the resolution.

Return this structure:

{{
    "manufacturer": null,
    "brand": null,
    "product_name": null,
    "model_number": null,
    "product_code": null,
    "upc": null,
    "ean": null,
    "gtin": null,

    "identity_resolution": {{
        "input_mpn": "{mfg_part_num}",
        "resolved_mpn": null,
        "resolved_manufacturer": null,
        "match_reason": null
    }},

    "product_type": null,
    "category": null,
    "subcategory": null,

    "classification": {{
        "dept": null,
        "class": null,
        "fine": null,
        "classpath": null
    }},

    "attributes": [
        {{
            "label": null,
            "value": null,
            "unit": null,
            "source_url": null
        }}
    ],

    "dimensions": {{
        "length": null,
        "width": null,
        "height": null,
        "depth": null,
        "unit": null,
        "source_url": null
    }},

    "weight": {{
        "value": null,
        "unit": null,
        "source_url": null
    }},

    "descriptions": {{
        "short": null,
        "long": null,
        "marketing": null
    }},

    "features": [],

    "evidence": [
        {{
            "url": null,
            "source_type": null,
            "description": null
        }}
    ],

    "source_discovery": {{
        "query_used": null,
        "sources_found": [],
        "primary_source": null
    }},

    "assets": {{
        "product_image": null,
        "specification_sheet": null,
        "installation_manual": null,
        "owners_manual": null
    }},

    "confidence": null,
    "notes": null
}}

IMPORTANT:
The "attributes" array should contain useful product specifications that
are actually found in the sources.

Examples:
- Voltage Rating → 120 V
- Sound Level → 47 dBA
- Material → Stainless Steel
- Number of Wash Cycles → 5
- Mounting Type → Built-in

These are examples only. Extract attributes appropriate to the actual
product.

Do not create attributes merely because the output schema has space for
them.

IMPORTANT IDENTIFIER EXAMPLES:
- If a source says "UPC: 008925172550", return:
    "upc": "008925172550"
  and do NOT return that value as "product_code".
- If a source says "Manufacturer Part Number: DCB518ASTS06G",
  return that identifier as the resolved manufacturer/model identifier.
- If a source says "Product Code: ABC123", that may be returned as
  "product_code": "ABC123".
- If an identifier's meaning is unclear, return null instead of guessing.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ]
            ),
        )

        raw_response = response.text.strip()

        # Remove Markdown JSON fences if returned.
        raw_response = re.sub(
            r"^```json\s*",
            "",
            raw_response,
            flags=re.IGNORECASE,
        )

        raw_response = re.sub(
            r"\s*```$",
            "",
            raw_response,
        )

        result = json.loads(raw_response)

        if not isinstance(result, dict):
            return {
                "status": "error",
                "message": "Gemini returned a non-object JSON response.",
            }

        return result

    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "message": f"Invalid JSON returned by Gemini: {e}",
            "raw_response": (
                raw_response
                if "raw_response" in locals()
                else None
            ),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }