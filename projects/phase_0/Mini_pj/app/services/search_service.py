from __future__ import annotations

from rapidfuzz import fuzz
from rank_bm25 import BM25Okapi

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.text_normalizer import TextNormalizer


class SearchService:
    BM25_MIN_SCORE = 0.8

    def __init__(
        self,
        product_repository: ProductRepository,
        normalizer: type[TextNormalizer] = TextNormalizer,
        fuzzy_threshold: float = 76.0,
    ) -> None:
        self.product_repository = product_repository
        self.normalizer = normalizer
        self.fuzzy_threshold = fuzzy_threshold
        self.synonyms = normalizer.get_synonym_groups()
        self._build_bm25_index()

    def _build_bm25_index(self) -> None:
        products = self.product_repository.list_all_with_comments()
        self.product_list = products
        corpus = [self._document_tokens(product) for product in products]
        self.bm25 = BM25Okapi(corpus) if corpus and any(corpus) else None

    def _document_tokens(self, product: Product) -> list[str]:
        text_parts = [
            product.normalized_name or "",
            product.normalized_description or "",
            self.normalizer.normalize_for_display(product.category),
        ]
        text_parts.extend(comment.normalized_content or "" for comment in product.comments)
        document_text = " ".join(part for part in text_parts if part)
        return self.normalizer.expand_with_synonyms(document_text).split()

    def search(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        normalized_query = self.normalizer.normalize_for_query(query)
        if len(normalized_query) < 2:
            return []

        query_variants = self.normalizer.expand_query_variants(normalized_query)
        expanded_query = self.normalizer.expand_with_synonyms(normalized_query)
        query_tokens = expanded_query.split()
        hits: dict[int, dict[str, object]] = {}

        if self.bm25 is not None and query_tokens:
            bm25_scores = self.bm25.get_scores(query_tokens)
            for idx, bm25_score in enumerate(bm25_scores):
                if bm25_score < self.BM25_MIN_SCORE:
                    continue
                product = self.product_list[idx]
                boost = self._intent_boost(product, normalized_query, query_variants, query)
                final_score = bm25_score * boost * 0.9
                hits[product.id] = self._to_result(product, final_score, "bm25")

        basic_candidates: dict[int, Product] = {}
        for variant in query_variants:
            if len(variant) < 2:
                continue
            for product in self.product_repository.search_basic(variant):
                basic_candidates[product.id] = product

        for product in basic_candidates.values():
            base_score = self._basic_score(product, query_variants)
            boost = self._intent_boost(product, normalized_query, query_variants, query)
            final_score = base_score * boost * 1.15

            if product.id not in hits or final_score > float(hits[product.id]["score"]):
                hits[product.id] = self._to_result(product, final_score, "basic")

        for product in self.product_list:
            if product.id in hits and float(hits[product.id]["score"]) > 80:
                continue

            fuzzy_score = self._fuzzy_score(product, query_variants)
            if fuzzy_score < self.fuzzy_threshold:
                continue

            boost = self._intent_boost(product, normalized_query, query_variants, query)
            final_score = fuzzy_score * boost * 0.85

            current = hits.get(product.id)
            if current is None or final_score > float(current["score"]):
                hits[product.id] = self._to_result(product, final_score, "fuzzy")

        results = sorted(
            hits.values(),
            key=lambda item: (-float(item["score"]), str(item["name"]).lower()),
        )
        return results[:limit]

    def _intent_boost(
        self,
        product: Product,
        normalized_query: str,
        query_variants: list[str],
        original_query: str,
    ) -> float:
        boost = 1.0
        name_norm = product.normalized_name or ""
        desc_norm = product.normalized_description or ""
        category_norm = self.normalizer.normalize_for_display(product.category)
        product_text = self.normalizer.expand_with_synonyms(
            f"{name_norm} {desc_norm} {category_norm}"
        )
        query_text = self.normalizer.expand_with_synonyms(" ".join(query_variants))

        for canonical, synonyms in self.synonyms.items():
            group_terms = (canonical, *synonyms)
            query_has_intent = any(
                self.normalizer.contains_phrase(query_text, term)
                for term in group_terms
            )
            product_has_intent = any(
                self.normalizer.contains_phrase(product_text, term)
                for term in group_terms
            )
            if query_has_intent and product_has_intent:
                boost += 1.3
                break

        strong_keywords = {
            "dau bung",
            "dau da day",
            "tieu hoa",
            "nhuan trang",
            "tao bon",
            "men vi sinh",
            "giam can",
            "tang chieu cao",
        }
        if any(
            self.normalizer.contains_phrase(product_text, keyword)
            for keyword in strong_keywords
        ):
            boost += 1.25

        original_query_norm = self.normalizer.normalize_for_display(original_query)
        category_keywords = {"tieu hoa", "nhuan trang", "vitamin", "canxi"}
        if self.normalizer.contains_phrase(original_query_norm, "thuoc") and any(
            self.normalizer.contains_phrase(category_norm, keyword)
            for keyword in category_keywords
        ):
            boost += 0.95

        query_words = {word for word in normalized_query.split() if len(word) >= 3}
        match_count = sum(
            1
            for word in query_words
            if self.normalizer.contains_phrase(name_norm, word)
            or self.normalizer.contains_phrase(desc_norm, word)
        )
        boost += match_count * 0.45

        return min(boost, 3.3)

    def _basic_score(self, product: Product, query_variants: list[str]) -> float:
        scores: list[float] = []
        name = product.normalized_name or ""
        desc = product.normalized_description or ""
        category = self.normalizer.normalize_for_display(product.category)

        for query in query_variants:
            if not query:
                continue
            if query == name:
                scores.append(100.0)
            elif self.normalizer.contains_phrase(name, query) or query in name:
                scores.append(96.0)

            if self.normalizer.contains_phrase(desc, query) or query in desc:
                scores.append(87.0)

            if self.normalizer.contains_phrase(category, query) or query in category:
                scores.append(84.0)

            for comment in product.comments:
                content = comment.normalized_content or ""
                if self.normalizer.contains_phrase(content, query) or query in content:
                    scores.append(80.0)

        if any(
            self.normalizer.contains_phrase(category, keyword)
            for keyword in ("tieu hoa", "nhuan trang", "tao bon")
        ):
            scores.append(86.0)

        return max(scores, default=67.0)

    def _fuzzy_score(self, product: Product, query_variants: list[str]) -> float:
        weighted_scores: list[float] = []
        fields: list[tuple[str | None, float]] = [
            (product.normalized_name, 1.0),
            (product.normalized_description, 0.83),
            (self.normalizer.normalize_for_display(product.category), 0.8),
        ]
        fields.extend((comment.normalized_content, 0.79) for comment in product.comments)

        for query in query_variants[:8]:
            for value, weight in fields:
                if not value:
                    continue
                field_score = max(
                    fuzz.WRatio(query, value),
                    fuzz.partial_ratio(query, value),
                    fuzz.token_set_ratio(query, value),
                )
                weighted_scores.append(field_score * weight)

        return round(max(weighted_scores, default=0.0), 2)

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
            "score": round(score, 2),
            "match_type": match_type,
        }
