import uuid
from datetime import datetime, timezone
from typing import List, Optional
from google.cloud import spanner
from app.db.repositories.base import BaseRepository
from app.models.domain.cart import CartItem

class CartRepository(BaseRepository):
    def get_cart(self, user_id: str) -> List[CartItem]:
        sql = """
            SELECT 
                c.UserId, c.ProductId, c.VariantId, c.Quantity, c.UpdatedAt,
                p.Name as ProductName, p.BasePrice as UnitPrice, 
                pv.Color, pv.Size
            FROM CartItems c
            JOIN Products p ON c.ProductId = p.ProductId
            JOIN ProductVariants pv ON c.ProductId = pv.ProductId AND c.VariantId = pv.VariantId
            WHERE c.UserId = @user_id
            ORDER BY c.UpdatedAt DESC
        """
        params = {"user_id": user_id}
        param_types = {"user_id": spanner.param_types.STRING}
        
        results = self.execute_sql(sql, params=params, param_types=param_types)
        
        items = []
        for row in results:
            items.append(CartItem(
                user_id=row[0],
                product_id=row[1],
                variant_id=row[2],
                quantity=row[3],
                updated_at=row[4],
                product_name=row[5],
                unit_price=row[6],
                color=row[7],
                size=row[8]
            ))
        return items

    def add_item(self, user_id: str, product_id: str, variant_id: str, quantity: int):
        updated_at = datetime.now(timezone.utc)
        
        def callback(transaction):
            # Check if item already exists
            results = transaction.execute_sql(
                "SELECT Quantity FROM CartItems WHERE UserId = @user_id AND ProductId = @product_id AND VariantId = @variant_id",
                params={"user_id": user_id, "product_id": product_id, "variant_id": variant_id},
                param_types={
                    "user_id": spanner.param_types.STRING,
                    "product_id": spanner.param_types.STRING,
                    "variant_id": spanner.param_types.STRING
                }
            )
            
            row = list(results)
            if row:
                new_quantity = row[0][0] + quantity
                transaction.update(
                    "CartItems",
                    columns=["UserId", "ProductId", "VariantId", "Quantity", "UpdatedAt"],
                    values=[[user_id, product_id, variant_id, new_quantity, updated_at]]
                )
            else:
                transaction.insert(
                    "CartItems",
                    columns=["UserId", "ProductId", "VariantId", "Quantity", "UpdatedAt"],
                    values=[[user_id, product_id, variant_id, quantity, updated_at]]
                )

        return self.database.run_in_transaction(callback)

    def remove_item(self, user_id: str, product_id: str, variant_id: str):
        def callback(transaction):
            transaction.delete(
                "CartItems",
                keyset=spanner.KeySet([[user_id, product_id, variant_id]])
            )
        
        return self.database.run_in_transaction(callback)

    def update_quantity(self, user_id: str, product_id: str, variant_id: str, quantity: int):
        updated_at = datetime.now(timezone.utc)
        def callback(transaction):
            transaction.update(
                "CartItems",
                columns=["UserId", "ProductId", "VariantId", "Quantity", "UpdatedAt"],
                values=[[user_id, product_id, variant_id, quantity, updated_at]]
            )
        
        return self.database.run_in_transaction(callback)
