from __future__ import annotations

from typing import Any

from src.models.schema import (
    Classification,
    Dimensions,
    Evidence,
    Measurement,
    Product,
    ProductAttribute,
    ProductContent,
)


def _none_if_empty(value: Any) -> Any:
    """Convert empty strings/lists/dicts to None where appropriate."""
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


def _build_attributes(
    data: dict[str, Any],
) -> list[ProductAttribute]:
    """Convert extracted attribute dictionaries into ProductAttribute objects."""

    attributes: list[ProductAttribute] = []

    for item in data.get("attributes") or []:
        if not isinstance(item, dict):
            continue

        label = _none_if_empty(item.get("label"))

        if not label:
            continue

        attributes.append(
            ProductAttribute(
                label=label,
                value=_none_if_empty(item.get("value")),
                unit=_none_if_empty(item.get("unit")),
                source_url=_none_if_empty(item.get("source_url")),
                confidence=item.get("confidence"),
            )
        )

    return attributes


def _build_evidence(
    data: dict[str, Any],
) -> list[Evidence]:
    """Convert extracted evidence dictionaries into Evidence objects."""

    evidence: list[Evidence] = []

    for item in data.get("evidence") or []:
        if not isinstance(item, dict):
            continue

        url = _none_if_empty(item.get("url"))

        if not url:
            continue

        evidence.append(
            Evidence(
                url=url,
                source_type=_none_if_empty(item.get("source_type")),
                description=_none_if_empty(item.get("description")),
            )
        )

    return evidence


def _build_classification(
    data: dict[str, Any],
) -> Classification | None:
    """Convert extracted classification data."""

    classification = data.get("classification") or {}

    if not isinstance(classification, dict):
        return None

    values = {
        "dept": _none_if_empty(classification.get("dept")),
        "class_name": _none_if_empty(classification.get("class")),
        "fine": _none_if_empty(classification.get("fine")),
        "classpath": _none_if_empty(classification.get("classpath")),
    }

    if not any(values.values()):
        return None

    return Classification(**values)


def _build_dimensions(
    data: dict[str, Any],
) -> Dimensions | None:
    """Convert extracted dimensions into the canonical model."""

    dimensions = data.get("dimensions") or {}

    if not isinstance(dimensions, dict):
        return None

    values = {
        "length": dimensions.get("length"),
        "width": dimensions.get("width"),
        "height": dimensions.get("height"),
        "unit": _none_if_empty(dimensions.get("unit")),
    }

    if not any(
        value is not None
        for value in values.values()
    ):
        return None

    return Dimensions(**values)


def _build_weight(
    data: dict[str, Any],
) -> Measurement | None:
    """Convert extracted weight into the canonical Measurement model."""

    weight = data.get("weight") or {}

    if not isinstance(weight, dict):
        return None

    value = weight.get("value")
    unit = _none_if_empty(weight.get("unit"))

    if value is None and unit is None:
        return None

    return Measurement(
        value=value,
        unit=unit,
    )


def _build_content(
    data: dict[str, Any],
) -> ProductContent | None:
    """Convert extracted descriptions/features into ProductContent."""

    descriptions = data.get("descriptions") or {}

    if not isinstance(descriptions, dict):
        descriptions = {}

    features = data.get("features") or []

    if not isinstance(features, list):
        features = []

    features = [
        str(feature).strip()
        for feature in features
        if feature is not None and str(feature).strip()
    ]

    values = {
        "short": _none_if_empty(descriptions.get("short")),
        "long": _none_if_empty(descriptions.get("long")),
        "marketing": _none_if_empty(descriptions.get("marketing")),
        "features": features,
    }

    if not any(
        [
            values["short"],
            values["long"],
            values["marketing"],
            features,
        ]
    ):
        return None

    return ProductContent(**values)


def product_from_extraction(
    data: dict[str, Any],
    *,
    source_fields: dict[str, str | None] | None = None,
) -> Product:
    """
    Convert an AI/fixture extraction dictionary into the canonical Product.

    This function does not perform web discovery, validation, or delivery
    formatting. It only translates extraction output into the Product model.
    """

    if not isinstance(data, dict):
        raise TypeError("Extraction result must be a dictionary.")

    identity = data.get("identity_resolution") or {}

    if not isinstance(identity, dict):
        identity = {}

    resolved_mpn = _none_if_empty(
        identity.get("resolved_mpn")
    )

    resolved_manufacturer = _none_if_empty(
        identity.get("resolved_manufacturer")
    )

    manufacturer = (
        _none_if_empty(data.get("manufacturer"))
        or resolved_manufacturer
    )

    # If the identity-resolution stage found a better MPN, prefer it.
    model_number = (
        _none_if_empty(data.get("model_number"))
        or resolved_mpn
    )

    product_code = (
        _none_if_empty(data.get("product_code"))
        or resolved_mpn
    )

    product = Product(
        product_name=_none_if_empty(
            data.get("product_name")
        ),

        brand=_none_if_empty(
            data.get("brand")
        ),

        manufacturer=manufacturer,

        model_number=model_number,

        product_code=product_code,

        product_type=_none_if_empty(
            data.get("product_type")
        ),

        category=_none_if_empty(
            data.get("category")
        ),

        subcategory=_none_if_empty(
            data.get("subcategory")
        ),

        classification=_build_classification(data),

        attributes=_build_attributes(data),

        dimensions=_build_dimensions(data),

        weight=_build_weight(data),

        content=_build_content(data),

        evidence=_build_evidence(data),

        source_fields=source_fields or {},

        product_image=_none_if_empty(
            (data.get("assets") or {}).get("product_image")
        ),

        specification_sheet=_none_if_empty(
            (data.get("assets") or {}).get("specification_sheet")
        ),
    )

    return product