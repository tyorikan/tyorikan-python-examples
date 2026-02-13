from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.domain.cart import CartItem

class CartItemCreate(BaseModel):
    product_id: str
    variant_id: str
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    product_id: str
    variant_id: str
    product_name: str
    color: str
    size: str
    unit_price: int
    quantity: int
    updated_at: datetime

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_amount: int
