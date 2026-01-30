from typing import List, Optional
from app.db.repositories.product import ProductRepository
from app.models.domain import Product

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def list_products(self, limit: int = 20, offset: int = 0) -> List[Product]:
        return self.repository.list_products(limit=limit, offset=offset)

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.repository.get_product(product_id)

    def create_product(self, product_data) -> str:
        # Convert schema to repo arguments
        variants_data = [v.model_dump() for v in product_data.variants]
        return self.repository.create_product(
            name=product_data.name,
            description=product_data.description,
            base_price=product_data.base_price,
            category_id=product_data.category_id,
            variants_data=variants_data
        )
