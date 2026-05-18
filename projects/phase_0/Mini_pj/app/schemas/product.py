from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CommentRead(BaseModel):
    id: int
    author: str | None = None
    rating: int | None = None
    content: str
    date: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductRead(BaseModel):
    id: int
    name: str
    url: str | None = None
    description: str | None = None
    category: str | None = None
    price: str | None = None
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductDetail(ProductRead):
    comments: list[CommentRead] = Field(default_factory=list)


class ProductSearchResult(BaseModel):
    id: int
    name: str
    url: str | None = None
    description: str | None = None
    category: str | None = None
    price: str | None = None
    source: str
    comments_count: int = 0
    comments: list[CommentRead] = Field(default_factory=list)
    score: float
    match_type: Literal["basic", "fuzzy", "bm25"]

    model_config = ConfigDict(from_attributes=True)


class ProductSearchResponse(BaseModel):
    query: str
    total: int
    results: list[ProductSearchResult]
