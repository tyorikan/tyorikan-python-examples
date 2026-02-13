from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.schemas.base import BaseResponse
from app.db.repositories.cart import CartRepository
from app.services.cart import CartService
from app.db.spanner import get_database

router = APIRouter()

# Fixed user ID for demo purposes
TEST_USER_ID = "test-user"

def get_cart_service(db = Depends(get_database)) -> CartService:
    repo = CartRepository(db)
    return CartService(repo)

@router.get("/", response_model=BaseResponse[CartResponse])
def get_cart(service: CartService = Depends(get_cart_service)):
    items = service.get_cart(TEST_USER_ID)
    total = sum(item.unit_price * item.quantity for item in items)
    
    # Map to schema
    item_responses = [
        CartItemResponse(
            product_id=item.product_id,
            variant_id=item.variant_id,
            product_name=item.product_name,
            color=item.color,
            size=item.size,
            unit_price=item.unit_price,
            quantity=item.quantity,
            updated_at=item.updated_at
        ) for item in items
    ]
    
    return BaseResponse(data=CartResponse(items=item_responses, total_amount=total))

@router.post("/", response_model=BaseResponse[dict])
def add_to_cart(
    item: CartItemCreate, 
    service: CartService = Depends(get_cart_service)
):
    service.add_to_cart(TEST_USER_ID, item.product_id, item.variant_id, item.quantity)
    return BaseResponse(data={"status": "added"})

@router.put("/{product_id}/{variant_id}", response_model=BaseResponse[dict])
def update_cart_item(
    product_id: str,
    variant_id: str,
    update: CartItemUpdate,
    service: CartService = Depends(get_cart_service)
):
    service.update_cart_item(TEST_USER_ID, product_id, variant_id, update.quantity)
    return BaseResponse(data={"status": "updated"})

@router.delete("/{product_id}/{variant_id}", response_model=BaseResponse[dict])
def remove_from_cart(
    product_id: str,
    variant_id: str,
    service: CartService = Depends(get_cart_service)
):
    service.remove_from_cart(TEST_USER_ID, product_id, variant_id)
    return BaseResponse(data={"status": "removed"})
