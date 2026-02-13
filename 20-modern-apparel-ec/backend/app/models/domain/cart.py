from datetime import datetime
from pydantic import BaseModel

class CartItem(BaseModel):
    user_id: str
    product_id: str
    variant_id: str
    quantity: int
    updated_at: datetime
    
    # Nested display data (optional, used for response)
    product_name: str = ""
    unit_price: int = 0
    color: str = ""
    size: str = ""
