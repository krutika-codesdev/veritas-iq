import sys

sys.path.insert(0, "src")

from processing.validator import (
    validate_field,
    validate_product,
)

from processing.health_score import (
    calculate_product_health_score,
)

def test_field_agreement():
    result = validate_field(
        "brand",
        [
            {
                "field": "brand",
                "value": "Diablo",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "brand",
                "value": "Diablo",
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
    )

    assert result["status"] == "agreement"
    assert result["agreement_count"] == 2
    assert result["source_count"] == 2
    assert result["confidence"] == 1.0


def test_field_conflict():
    result = validate_field(
        "brand",
        [
            {
                "field": "brand",
                "value": "Diablo",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "brand",
                "value": "Freud",
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
    )

    assert result["status"] == "conflict"
    assert result["agreement_count"] == 1
    assert result["source_count"] == 2
    assert result["confidence"] == 0.5


def test_field_partial():
    result = validate_field(
        "brand",
        [
            {
                "field": "brand",
                "value": "Diablo",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "brand",
                "value": None,
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
    )

    assert result["status"] == "partial"
    assert result["agreement_count"] == 1
    assert result["source_count"] == 1
    assert result["confidence"] == 1.0


def test_field_missing():
    result = validate_field(
        "brand",
        [
            {
                "field": "brand",
                "value": None,
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "brand",
                "value": None,
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
    )

    assert result["status"] == "missing"
    assert result["agreement_count"] == 0
    assert result["source_count"] == 0
    assert result["confidence"] == 0.0


def test_identifier_agreement():
    result = validate_field(
        "gtin",
        [
            {
                "field": "gtin",
                "value": "0008925172550",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "gtin",
                "value": "0008925172550",
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
    )

    assert result["status"] == "agreement"
    assert result["agreement_count"] == 2
    assert result["source_count"] == 2
    assert result["confidence"] == 1.0


def test_product_validation():
    observations = {
        "brand": [
            {
                "field": "brand",
                "value": "Diablo",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "brand",
                "value": "Diablo",
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
        "gtin": [
            {
                "field": "gtin",
                "value": "0008925172550",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "gtin",
                "value": "0008925172550",
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
        "manufacturer": [
            {
                "field": "manufacturer",
                "value": "Diablo",
                "source_url": "https://manufacturer.example",
                "source_type": "manufacturer",
            },
            {
                "field": "manufacturer",
                "value": None,
                "source_url": "https://distributor.example",
                "source_type": "distributor",
            },
        ],
    }

    result = validate_product(observations)

    assert result["brand"]["status"] == "agreement"
    assert result["gtin"]["status"] == "agreement"
    assert result["manufacturer"]["status"] == "partial"

    assert len(result) == 3

def test_product_health_score():
    validation_results = {
        "brand": {
            "status": "agreement",
            "agreement_count": 2,
            "source_count": 2,
            "evidence": [
                {
                    "source_url": "https://manufacturer.example",
                },
                {
                    "source_url": "https://distributor.example",
                },
            ],
        },
        "gtin": {
            "status": "agreement",
            "agreement_count": 2,
            "source_count": 2,
            "evidence": [
                {
                    "source_url": "https://manufacturer.example",
                },
                {
                    "source_url": "https://distributor.example",
                },
            ],
        },
        "manufacturer": {
            "status": "partial",
            "agreement_count": 1,
            "source_count": 1,
            "evidence": [
                {
                    "source_url": "https://manufacturer.example",
                },
            ],
        },
        "weight": {
            "status": "missing",
            "agreement_count": 0,
            "source_count": 0,
            "evidence": [],
        },
    }

    required_fields = [
        "brand",
        "gtin",
        "manufacturer",
        "weight",
    ]

    result = calculate_product_health_score(
        validation_results,
        required_fields,
    )

    print("\nPRODUCT HEALTH SCORE")
    print(result)

    assert result["components"]["agreement"] == 62.5
    assert result["components"]["completeness"] == 75.0
    assert result["components"]["evidence"] == 100.0

    assert result["score"] == 77.5

def test_product_field_evidence_is_preserved():
    from ai.product_adapter import product_from_extraction

    extraction = {
        "product_name": "Diablo Example Product",
        "brand": "Diablo",
        "gtin": "0008925172550",
        "field_evidence": {
            "brand": [
                {
                    "url": "https://manufacturer.example/product",
                    "source_type": "manufacturer",
                    "description": "Official manufacturer product page",
                }
            ],
            "gtin": [
                {
                    "url": "https://manufacturer.example/spec",
                    "source_type": "manufacturer",
                    "description": "Manufacturer specification page",
                }
            ],
        },
    }

    product = product_from_extraction(extraction)

    assert "brand" in product.field_evidence
    assert "gtin" in product.field_evidence

    assert (
        product.field_evidence["brand"][0].url
        == "https://manufacturer.example/product"
    )

    assert (
        product.field_evidence["gtin"][0].url
        == "https://manufacturer.example/spec"
    )