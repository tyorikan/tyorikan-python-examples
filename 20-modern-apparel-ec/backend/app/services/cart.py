from typing import List
from app.db.repositories.cart import CartRepository
from app.models.domain.cart import CartItem

class CartService:
    def __init__(self, repository: CartRepository):
        self.repository = repository

    def get_cart(self, user_id: str) -> List[CartItem]:
        return self.repository.get_cart(user_id)

    def add_to_cart(self, user_id: str, product_id: str, variant_id: str, quantity: int):
        return self.repository.add_item(user_id, product_id, variant_id, quantity)

    def remove_from_cart(self, user_id: str, product_id: str, variant_id: str):
        return self.repository.remove_item(user_id, product_id, variant_id)

    def update_cart_item(self, user_id: str, product_id: str, variant_id: str, quantity: int):
        return self.repository.update_quantity(user_id, product_id, variant_id, quantity)
