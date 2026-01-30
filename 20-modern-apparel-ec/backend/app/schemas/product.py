from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductVariantCreate(BaseModel):
    variant_id: str
    color: str
    size: str
    stock_quantity: int

class ProductCreate(BaseModel):
    name: str
    description: str
    base_price: int
    category_id: str
    variants: List[ProductVariantCreate] = []

class ProductVariantResponse(BaseModel):
    variant_id: str
    color: str
    size: str
    stock_quantity: int
    product_id: str

class ProductResponse(BaseModel):
    product_id: str
    name: str
    description: str
    base_price: int
    category_id: str
    created_at: datetime
    variants: List[ProductVariantResponse] = []
