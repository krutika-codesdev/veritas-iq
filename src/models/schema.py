from pydantic import BaseModel


class Product(BaseModel):
    product_name: str | None = None
    manufacturer: str | None = None
    category: str | None = None
    material: str | None = None
    pressure_rating: str | None = None
    weight: str | None = None
    warranty: str | None = None