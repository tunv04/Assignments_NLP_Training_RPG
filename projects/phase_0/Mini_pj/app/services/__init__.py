from app.services.text_normalizer import TextNormalizer

__all__ = ["SearchService", "TextNormalizer"]


def __getattr__(name: str):
    if name == "SearchService":
        from app.services.search_service import SearchService

        return SearchService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
