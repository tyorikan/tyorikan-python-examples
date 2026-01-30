import uuid
from datetime import datetime, timezone
from typing import List, Optional
from google.cloud import spanner
from app.db.repositories.base import BaseRepository
from app.models.domain import Product, ProductVariant

class ProductRepository(BaseRepository):
    def list_products(self, limit: int = 10, offset: int = 0) -> List[Product]:
        sql = """
            SELECT 
                p.ProductId, p.Name, p.Description, p.BasePrice, p.CategoryId, p.CreatedAt,
                ARRAY(
                    SELECT AS STRUCT pv.VariantId, pv.Color, pv.Size, pv.StockQuantity
                    FROM ProductVariants pv
                    WHERE pv.ProductId = p.ProductId
                ) as Variants
            FROM Products p
            ORDER BY p.CreatedAt DESC
            LIMIT @limit OFFSET @offset
        """
        params = {"limit": limit, "offset": offset}
        param_types = {"limit": spanner.param_types.INT64, "offset": spanner.param_types.INT64}
        
        results = self.execute_sql(sql, params=params, param_types=param_types)
        
        products = []
        for row in results:
            variants = [
                ProductVariant(
                    product_id=row[0],
                    variant_id=v[0],
                    color=v[1],
                    size=v[2],
                    stock_quantity=v[3]
                ) for v in row[6]
            ]
            products.append(Product(
                product_id=row[0],
                name=row[1],
                description=row[2],
                base_price=row[3],
                category_id=row[4],
                created_at=row[5],
                variants=variants
            ))
        return products

    def create_product(self, name: str, description: str, base_price: int, category_id: str, variants_data: List[dict]):
        product_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        
        def callback(transaction):
            # Insert Product
            transaction.insert(
                "Products",
                columns=["ProductId", "Name", "Description", "BasePrice", "CategoryId", "CreatedAt"],
                values=[[product_id, name, description, base_price, category_id, created_at]]
            )
            
            # Insert Variants
            if variants_data:
                variant_rows = []
                for v in variants_data:
                    variant_id = v.get("variant_id") or str(uuid.uuid4())
                    variant_rows.append([
                        product_id,
                        variant_id,
                        v["color"],
                        v["size"],
                        v["stock_quantity"]
                    ])
                
                transaction.insert(
                    "ProductVariants",
                    columns=["ProductId", "VariantId", "Color", "Size", "StockQuantity"],
                    values=variant_rows
                )
            return product_id

        return self.database.run_in_transaction(callback)

    def get_product(self, product_id: str) -> Optional[Product]:
        sql = """
            SELECT 
                p.ProductId, p.Name, p.Description, p.BasePrice, p.CategoryId, p.CreatedAt,
                ARRAY(
                    SELECT AS STRUCT pv.VariantId, pv.Color, pv.Size, pv.StockQuantity
                    FROM ProductVariants pv
                    WHERE pv.ProductId = p.ProductId
                ) as Variants
            FROM Products p
            WHERE p.ProductId = @product_id
        """
        params = {"product_id": product_id}
        param_types = {"product_id": spanner.param_types.STRING}
        
        results = list(self.execute_sql(sql, params=params, param_types=param_types))
        if not results:
            return None
        
        row = results[0]
        variants = [
            ProductVariant(
                product_id=row[0],
                variant_id=v[0],
                color=v[1],
                size=v[2],
                stock_quantity=v[3]
            ) for v in row[6]
        ]
        return Product(
            product_id=row[0],
            name=row[1],
            description=row[2],
            base_price=row[3],
            category_id=row[4],
            created_at=row[5],
            variants=variants
        )
