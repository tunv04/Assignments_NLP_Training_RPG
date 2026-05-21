from __future__ import annotations

import math
from collections import Counter

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.text_normalizer import TextNormalizer


class SearchService:
    """
    Document retrieval pipeline:
    preprocess documents -> compute TF-IDF -> vectorize query
    -> compute cosine similarity -> rank documents.
    """

    def __init__(
        self,
        product_repository: ProductRepository,
        normalizer: type[TextNormalizer] = TextNormalizer,
        min_similarity: float = 0.0,
    ) -> None:
        self.product_repository = product_repository
        self.normalizer = normalizer
        self.min_similarity = min_similarity
        self._build_tfidf_index()

    def _build_tfidf_index(self) -> None:
        self.product_list = self.product_repository.list_all_with_comments()
        self.document_tokens = [
            self._document_tokens(product) for product in self.product_list
        ]
        self.idf = self._compute_idf(self.document_tokens)
        self.document_vectors = [
            self._tfidf_vector(tokens) for tokens in self.document_tokens
        ]
        self.document_norms = [
            self._vector_norm(vector) for vector in self.document_vectors
        ]

    def _document_tokens(self, product: Product) -> list[str]:
        text_parts = [
            product.name or "",
            product.description or "",
            product.category or "",
        ]
        text_parts.extend(comment.content or "" for comment in product.comments)
        document_text = " ".join(part for part in text_parts if part)
        return self.normalizer.normalize_for_index(document_text).split()

    @staticmethod
    def _compute_idf(corpus: list[list[str]]) -> dict[str, float]:
        document_count = len(corpus)
        document_frequency: Counter[str] = Counter()

        for tokens in corpus:
            document_frequency.update(set(tokens))

        return {
            term: math.log((document_count + 1) / (frequency + 1)) + 1.0
            for term, frequency in document_frequency.items()
        }

    def _tfidf_vector(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}

        term_frequency = Counter(tokens)
        token_count = len(tokens)
        vector: dict[str, float] = {}

        for term, frequency in term_frequency.items():
            idf = self.idf.get(term)
            if idf is None:
                continue
            tf = frequency / token_count
            vector[term] = tf * idf

        return vector

    @staticmethod
    def _vector_norm(vector: dict[str, float]) -> float:
        return math.sqrt(sum(weight * weight for weight in vector.values()))

    @staticmethod
    def _cosine_similarity(
        vector_a: dict[str, float],
        norm_a: float,
        vector_b: dict[str, float],
        norm_b: float,
    ) -> float:
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        dot_product = sum(
            weight * vector_b.get(term, 0.0)
            for term, weight in vector_a.items()
        )
        return dot_product / (norm_a * norm_b)

    def search(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        normalized_query = self.normalizer.normalize_for_query(query)
        query_tokens = normalized_query.split()
        if not query_tokens:
            return []

        query_vector = self._tfidf_vector(query_tokens)
        query_norm = self._vector_norm(query_vector)
        if query_norm == 0.0:
            return []

        hits: list[dict[str, object]] = []
        for product, document_vector, document_norm in zip(
            self.product_list,
            self.document_vectors,
            self.document_norms,
        ):
            score = self._cosine_similarity(
                query_vector,
                query_norm,
                document_vector,
                document_norm,
            )
            if score <= self.min_similarity:
                continue
            hits.append(self._to_result(product, score, "tfidf_cosine"))

        results = sorted(
            hits,
            key=lambda item: (-float(item["score"]), str(item["name"]).lower()),
        )
        return results[:limit]

    @staticmethod
    def _to_result(
        product: Product,
        score: float,
        match_type: str,
    ) -> dict[str, object]:
        comments = list(product.comments)
        return {
            "id": product.id,
            "name": product.name,
            "url": product.url,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "source": product.source,
            "comments_count": len(comments),
            "comments": [
                {
                    "id": comment.id,
                    "author": getattr(comment, "author", None),
                    "rating": getattr(comment, "rating", None),
                    "content": comment.content,
                    "date": getattr(comment, "date", None),
                }
                for comment in comments[:3]
            ],
            "score": round(score, 4),
            "match_type": match_type,
        }
