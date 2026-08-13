from pydantic import BaseModel, Field


class Measurement(BaseModel):
    value: float | None = None
    unit: str | None = None
    qualifier: str | None = None


class Dimensions(BaseModel):
    length: float | None = None
    width: float | None = None
    height: float | None = None
    unit: str | None = None


class Warranty(BaseModel):
    duration: str | None = None
    type: str | None = None
    coverage: str | None = None
    exclusions: list[str] = Field(default_factory=list)
    provider: str | None = None


class Money(BaseModel):
    value: float | None = None
    currency: str | None = None


class ProductAttribute(BaseModel):
    """A flexible product attribute used by the UniHack catalogue model."""

    label: str
    value: str | float | int | None = None
    unit: str | None = None
    source_url: str | None = None
    confidence: float | None = None


class Evidence(BaseModel):
    """Source supporting a product or attribute."""

    url: str
    source_type: str | None = None
    description: str | None = None


class Classification(BaseModel):
    dept: str | None = None
    class_name: str | None = None
    fine: str | None = None
    classpath: str | None = None


class ProductContent(BaseModel):
    mobile: str | None = None
    invoice: str | None = None
    short: str | None = None
    long: str | None = None
    retail: str | None = None
    marketing: str | None = None
    features: list[str] = Field(default_factory=list)


class Product(BaseModel):
    # Existing VeritasIQ identity fields
    product_name: str | None = None
    brand: str | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    product_code: str | None = None

    # Existing/general product fields
    product_type: str | None = None
    category: str | None = None
    subcategory: str | None = None

    country_of_origin: str | None = None
    intended_use: str | None = None

    dimensions: Dimensions | None = None
    weight: Measurement | None = None
    material: str | None = None
    color: list[str] = Field(default_factory=list)
    size: str | None = None

    price: Money | None = None

    warranty: Warranty | None = None

    certifications: list[str] = Field(default_factory=list)
    included_items: list[str] = Field(default_factory=list)

    # UniHack enrichment fields
    classification: Classification | None = None
    attributes: list[ProductAttribute] = Field(default_factory=list)
    content: ProductContent | None = None
    evidence: list[Evidence] = Field(default_factory=list)

    # Preserve the original six-column UniHack input.
    source_fields: dict[str, str | None] = Field(default_factory=dict)

    trade_name: str | None = None

    part_number: str | None = None
    sku: str | None = None
    alternate_part_number: str | None = None

    with_text: str | None = None
    standard_approvals: str | None = None

    product_image: str | None = None
    alternate_images: list[str] = Field(default_factory=list)
    specification_sheet: str | None = None

    actual_image: bool | None = None