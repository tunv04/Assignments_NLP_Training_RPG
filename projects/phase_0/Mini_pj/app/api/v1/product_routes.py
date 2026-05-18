from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductDetail, ProductRead, ProductSearchResponse
from app.services.search_service import SearchService


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
def list_products(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    repository = ProductRepository(db)
    return repository.list_products(limit=limit, offset=offset)


@router.get("/search", response_model=ProductSearchResponse)
def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> ProductSearchResponse:
    repository = ProductRepository(db)
    service = SearchService(repository)
    results = service.search(query=q, limit=limit)
    return ProductSearchResponse(query=q, total=len(results), results=results)


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductDetail:
    repository = ProductRepository(db)
    product = repository.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product
