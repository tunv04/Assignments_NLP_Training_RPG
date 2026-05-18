from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.product import Comment, Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(self, limit: int = 20, offset: int = 0) -> list[Product]:
        return (
            self.db.query(Product)
            .order_by(Product.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .options(selectinload(Product.comments))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_url(self, url: str) -> Product | None:
        return (
            self.db.query(Product)
            .options(selectinload(Product.comments))
            .filter(Product.url == url)
            .first()
        )

    def search_basic(self, normalized_query: str) -> list[Product]:
        pattern = f"%{normalized_query}%"
        return (
            self.db.query(Product)
            .options(selectinload(Product.comments))
            .outerjoin(Comment, Product.id == Comment.product_id)
            .filter(
                or_(
                    Product.normalized_name.like(pattern),
                    Product.normalized_description.like(pattern),
                    Comment.normalized_content.like(pattern),
                )
            )
            .distinct()
            .all()
        )

    def list_all_with_comments(self) -> list[Product]:
        return (
            self.db.query(Product)
            .options(selectinload(Product.comments))
            .order_by(Product.id.asc())
            .all()
        )

    def upsert_product(
        self,
        product_data: dict[str, str | None],
        comments: list[dict[str, object]],
    ) -> tuple[Product, bool]:
        url = product_data.get("url")
        product = self.get_by_url(url) if url else None
        created = product is None

        if product is None:
            product = Product(**product_data)
            self.db.add(product)
        else:
            for field, value in product_data.items():
                setattr(product, field, value)
            product.comments.clear()
            self.db.flush()

        for comment_data in comments:
            product.comments.append(Comment(**comment_data))

        return product, created
