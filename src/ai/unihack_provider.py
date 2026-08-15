from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from src.ai.product_adapter import product_from_extraction
from src.ai.unihack_extractor import extract_unihack_product
from src.models.schema import Product


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_FIXTURE_DIR = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
)


def _find_fixture(
    mfg_part_num: str,
) -> Path:
    """
    Find a development fixture for the supplied MPN.

    The fixture directory may use either:
    1. the exact MPN as the filename, or
    2. a normalized/simplified filename.

    This keeps fixture naming separate from product identity.
    """

    # First try the exact MPN.
    exact_path = (
        DEFAULT_FIXTURE_DIR
        / f"{mfg_part_num}.json"
    )

    if exact_path.exists():
        return exact_path

    # Then try a normalized filename.
    normalized = "".join(
        character.lower()
        if character.isalnum()
        else "_"
        for character in mfg_part_num
    )

    normalized_path = (
        DEFAULT_FIXTURE_DIR
        / f"{normalized}.json"
    )

    if normalized_path.exists():
        return normalized_path

    # Finally, support the existing 3M fixture convention:
    # 3MABR-7100075678 → 3m_7100075678.json
    if "-" in mfg_part_num:
        suffix = mfg_part_num.rsplit("-", 1)[-1]

        manufacturer_prefix = (
            mfg_part_num.split("-", 1)[0]
        )

        # The existing fixture uses:
        # 3m_<manufacturer-part-number>.json
        simplified_path = (
            DEFAULT_FIXTURE_DIR
            / f"{manufacturer_prefix[:2].lower()}_{suffix}.json"
        )

        if simplified_path.exists():
            return simplified_path

    raise FileNotFoundError(
        f"No enrichment fixture found for MPN "
        f"'{mfg_part_num}'.\n"
        f"Expected fixture directory: "
        f"{DEFAULT_FIXTURE_DIR}"
    )


def _load_fixture(
    mfg_part_num: str,
) -> dict[str, Any]:
    """Load a source-backed extraction fixture."""

    path = _find_fixture(mfg_part_num)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            f"Fixture must contain a JSON object: {path}"
        )

    return data


def extract_with_fixture(
    mfg_part_num: str,
    part_desc: str,
    part_manuf: str | None = None,
) -> dict[str, Any]:
    """
    Load a source-backed extraction fixture.

    The input arguments are retained for compatibility with
    the Gemini provider interface.
    """

    return _load_fixture(mfg_part_num)


def extract_with_gemini(
    mfg_part_num: str,
    part_desc: str,
    part_manuf: str | None = None,
) -> dict[str, Any]:
    """Run the existing Gemini UniHack extractor."""

    return extract_unihack_product(
        mfg_part_num=mfg_part_num,
        part_desc=part_desc,
        part_manuf=part_manuf,
    )


def extract_unihack(
    mfg_part_num: str,
    part_desc: str,
    part_manuf: str | None = None,
) -> dict[str, Any]:
    """
    Extract UniHack product data using the configured provider.

    Supported providers:
        fixture
        gemini

    Default:
        fixture
    """

    provider = os.getenv(
        "UNIHACK_PROVIDER",
        "fixture",
    ).strip().lower()

    if provider == "fixture":
        return extract_with_fixture(
            mfg_part_num=mfg_part_num,
            part_desc=part_desc,
            part_manuf=part_manuf,
        )

    if provider == "gemini":
        return extract_with_gemini(
            mfg_part_num=mfg_part_num,
            part_desc=part_desc,
            part_manuf=part_manuf,
        )

    raise ValueError(
        f"Unsupported UNIHACK_PROVIDER: '{provider}'. "
        "Use 'fixture' or 'gemini'."
    )


def enrich_unihack_product(
    mfg_part_num: str,
    part_desc: str,
    part_manuf: str | None = None,
    source_fields: dict[str, str | None] | None = None,
) -> Product:
    """
    Complete UniHack enrichment entry point.

    Provider extraction:
        fixture or Gemini
            ↓
    extraction dictionary
            ↓
    canonical Product
    """

    extraction = extract_unihack(
        mfg_part_num=mfg_part_num,
        part_desc=part_desc,
        part_manuf=part_manuf,
    )

    if (
        isinstance(extraction, dict)
        and extraction.get("status") == "error"
    ):
        raise RuntimeError(
            extraction.get(
                "message",
                "UniHack enrichment provider failed.",
            )
        )

    return product_from_extraction(
        extraction,
        source_fields=source_fields,
    )