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


class Product(BaseModel):
    product_name: str | None = None
    brand: str | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    product_code: str | None = None

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


class Money(BaseModel):
    value: float | None = None
    currency: str | None = None


