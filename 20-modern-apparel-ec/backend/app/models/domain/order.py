from datetime import datetime
from typing import List
from pydantic import BaseModel

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
