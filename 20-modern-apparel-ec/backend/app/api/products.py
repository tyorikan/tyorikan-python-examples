from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.base import BaseResponse, MetaData
from app.db.repositories.product import ProductRepository
from app.services.product import ProductService
from app.db.spanner import get_database

router = APIRouter()

def get_product_service(db = Depends(get_database)) -> ProductService:
    repo = ProductRepository(db)
    return ProductService(repo)

@router.get("/", response_model=BaseResponse[List[ProductResponse]])
def list_products(
    limit: int = 20, 
    offset: int = 0, 
    service: ProductService = Depends(get_product_service)
):
    products = service.list_products(limit=limit, offset=offset)
    return BaseResponse(
        data=products,
        meta=MetaData(page=offset // limit + 1, total=len(products)) # Simplification
    )

@router.post("/", response_model=BaseResponse[dict])
def create_product(
    product: ProductCreate, 
    service: ProductService = Depends(get_product_service)
):
    product_id = service.create_product(product)
    return BaseResponse(data={"product_id": product_id, "status": "created"})

@router.get("/{product_id}", response_model=BaseResponse[ProductResponse])
def get_product(
    product_id: str, 
    service: ProductService = Depends(get_product_service)
):
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return BaseResponse(data=product)

