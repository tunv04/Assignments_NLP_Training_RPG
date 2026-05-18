from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    url: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    normalized_description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String)
    price: Mapped[str | None] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, default="chiaki.vn")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_content: Mapped[str] = mapped_column(Text, nullable=False)

    # date gốc từ JSON, ví dụ: "13:53, 05/04/2026"
    date: Mapped[str | None] = mapped_column(String, nullable=True)

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="comments",
    )
