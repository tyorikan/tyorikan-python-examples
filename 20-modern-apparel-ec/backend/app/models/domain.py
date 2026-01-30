from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: str
    email: str
    password_hash: str
    name: str
    created_at: datetime

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

class OrderItem(BaseModel):
    order_id: str
    item_id: int
    product_id: str
    variant_id: str
    quantity: int
    unit_price: int

class Order(BaseModel):
    order_id: str
    user_id: str
    total_amount: int
    status: str
    created_at: datetime
    items: List[OrderItem] = []
