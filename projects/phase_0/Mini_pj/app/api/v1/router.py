from fastapi import APIRouter

from app.api.v1 import product_routes


api_router = APIRouter()
api_router.include_router(product_routes.router)
