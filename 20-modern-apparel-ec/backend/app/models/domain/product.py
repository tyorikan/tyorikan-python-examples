from datetime import datetime
from typing import List
from pydantic import BaseModel

class ProductVariant(BaseModel):
    product_id: str
    variant_id: str
    color: str
    size: str
    stock_quantity: int

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    base_price: int
    category_id: str
    created_at: datetime
    variants: List[ProductVariant] = []
