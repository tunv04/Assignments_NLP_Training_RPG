"""raw text
-> clean HTML / Unicode / lowercase / bỏ dấu
-> tokenize thành từng token
-> sửa lỗi gõ / viết tắt
-> bỏ stop words
-> ghép lại thành normalized_text
raw text
-> clean HTML / Unicode / lowercase / bỏ dấu
-> tokenize thành từng token
-> sửa lỗi gõ / viết tắt
-> bỏ stop words
-> ghép lại thành normalized_text
"""
from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class PreprocessResult:
    raw_text: str
    cleaned_text: str
    tokens: list[str]
    normalized_text: str


class TextNormalizer:
    """
    Pipeline tiền xử lý text cho bài toán search sản phẩm:
    raw text -> HTML cleanup -> unicode/accent normalization -> tokenization
    -> viết tắt/lỗi gõ phổ biến -> stop-word removal -> normalized text.
    """

    HTML_TAG_RE = re.compile(r"<[^>]+>")
    NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")
    WHITESPACE_RE = re.compile(r"\s+")
    TOKEN_RE = re.compile(r"[a-z0-9]+")

    # Stop words đã ở dạng không dấu vì pipeline remove accent trước.
    STOP_WORDS: set[str] = {
        "thuoc",
        "vien",
        "uong",
        "dung",
        "su",
        "cho",
        "cua",
        "va",
        "la",
        "voi",
        "mot",
        "cac",
        "nay",
        "do",
        "ra",
        "sang",
        "tot",
        "nhat",
        "hieu",
        "qua",
        "san",
        "pham",
        "thuc",
        "chuc",
        "nang",
        "ho",
        "tro",
        "loai",
        "hop",
        "goi",
        "chai",
        "tuyp",
    }

    # Chuẩn hóa lỗi gõ/viết tắt ở mức token, không thay thế synonym nghiệp vụ.
    TOKEN_REPLACEMENTS: dict[str, str] = {
        "k": "khong",
        "ko": "khong",
        "khg": "khong",
        "sp": "san pham",
        "tpcn": "thuc pham chuc nang",
        "tpbvsk": "thuc pham bao ve suc khoe",
        "sd": "su dung",
        "vitmin": "vitamin",
        "vitamine": "vitamin",
        "taobon": "tao bon",
        "omega3": "omega 3",
        "omega03": "omega 3",
    }

    PHRASE_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
        (re.compile(r"\btao\s*bon\b"), "tao bon"),
        (re.compile(r"\bvit\s*min\b"), "vitamin"),
        (re.compile(r"\bomega\s*0?3\b"), "omega 3"),
        (re.compile(r"\bdau\s*buong\b"), "dau bung"),
        (re.compile(r"\bdau\s*thung\s*bung\b"), "dau bung"),
        (re.compile(r"\btron\s*bung\b"), "truong bung"),
        (re.compile(r"\bkho\s*tieu\s*hoa\b"), "kho tieu"),
    )

    # Nhóm synonym domain để search mở rộng query/corpus, không ghi đè text gốc.
    DOMAIN_SYNONYM_GROUPS: dict[str, tuple[str, ...]] = {
        "dau bung": (
            "dau da day",
            "kho tieu",
            "day hoi",
            "chuong bung",
            "truong bung",
        ),
        "tieu hoa": (
            "nhuan trang",
            "tao bon",
            "tieu chay",
            "phan mem",
            "kho tieu",
        ),
        "men vi sinh": (
            "probiotic",
            "probiotics",
            "loi khuan",
            "sinh khuan",
            "men probiotic",
        ),
        "giam can": (
            "giam mo",
            "dot mo",
            "giam beo",
            "giam mo bung",
        ),
        "tang chieu cao": (
            "phat trien chieu cao",
            "cao hon",
            "tang cao",
        ),
        "tang suc de khang": (
            "tang mien dich",
            "bo sung mien dich",
            "tang de khang",
            "mien dich",
            "de khang",
        ),
        "vitamin": (
            "vitamin c",
            "vitamin d",
            "vitamin d3",
            "vitamin k2",
            "multi vitamin",
            "multivitamin",
        ),
        "omega 3": (
            "omega",
            "fish oil",
            "dau ca",
            "dha",
            "epa",
        ),
        "magie": (
            "magnesium",
            "magie glycinate",
        ),
        "canxi": (
            "calcium",
            "calci",
        ),
    }

    @staticmethod
    def _to_text(text: object) -> str:
        if text is None:
            return ""
        return str(text)

    @staticmethod
    def remove_accents(text: object) -> str:
        if text is None:
            return ""

        value = str(text).replace("Đ", "D").replace("đ", "d")
        normalized = unicodedata.normalize("NFD", value)
        return "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )

    @classmethod
    def clean_text(cls, text: object) -> str:
        value = html.unescape(cls._to_text(text))
        value = cls.HTML_TAG_RE.sub(" ", value)
        value = unicodedata.normalize("NFKC", value)
        value = cls.remove_accents(value).lower()
        value = value.replace("\u00a0", " ")
        value = cls.NON_ALNUM_RE.sub(" ", value)
        value = cls.WHITESPACE_RE.sub(" ", value).strip()

        for pattern, replacement in cls.PHRASE_REPLACEMENTS:
            value = pattern.sub(replacement, value)

        return cls.WHITESPACE_RE.sub(" ", value).strip()

    @classmethod
    def tokenize(cls, text: object) -> list[str]:
        return cls.TOKEN_RE.findall(cls.clean_text(text))

    @classmethod
    def _apply_token_replacements(cls, tokens: list[str]) -> list[str]:
        expanded_tokens: list[str] = []
        for token in tokens:
            replacement = cls.TOKEN_REPLACEMENTS.get(token, token)
            expanded_tokens.extend(replacement.split())
        return expanded_tokens

    @classmethod
    def preprocess(
        cls,
        text: object,
        *,
        remove_stop_words: bool = True,
    ) -> PreprocessResult:
        raw_text = cls._to_text(text)
        cleaned_text = cls.clean_text(raw_text)
        tokens = cls._apply_token_replacements(cls.TOKEN_RE.findall(cleaned_text))

        if remove_stop_words:
            tokens = [token for token in tokens if token not in cls.STOP_WORDS]

        normalized_text = " ".join(tokens)
        return PreprocessResult(
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            tokens=tokens,
            normalized_text=normalized_text,
        )

    @classmethod
    def normalize(cls, text: object) -> str:
        return cls.preprocess(text).normalized_text

    @classmethod
    def normalize_for_index(cls, text: object) -> str:
        return cls.preprocess(text).normalized_text

    @classmethod
    def normalize_for_query(cls, text: object) -> str:
        return cls.preprocess(text).normalized_text

    @classmethod
    def normalize_for_display(cls, text: object) -> str:
        return cls.preprocess(text, remove_stop_words=False).normalized_text

    @classmethod
    def get_keywords(cls, text: object) -> list[str]:
        normalized = cls.normalize(text)
        return [word for word in normalized.split() if len(word) > 1]

    @staticmethod
    def contains_phrase(text: str, phrase: str) -> bool:
        if not text or not phrase:
            return False
        return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None

    @staticmethod
    def replace_phrase(text: str, old: str, new: str) -> str:
        return re.sub(rf"(?<!\w){re.escape(old)}(?!\w)", new, text)

    @classmethod
    def get_synonym_groups(cls) -> dict[str, tuple[str, ...]]:
        return cls.DOMAIN_SYNONYM_GROUPS

    @classmethod
    def expand_with_synonyms(cls, normalized_text: str) -> str:
        """
        Mở rộng text đã normalize bằng synonym cùng domain.
        Dùng cho BM25/query expansion, không dùng để lưu đè dữ liệu gốc.
        """
        if not normalized_text:
            return ""

        additions: list[str] = []
        for canonical, synonyms in cls.DOMAIN_SYNONYM_GROUPS.items():
            group_terms = (canonical, *synonyms)
            if any(cls.contains_phrase(normalized_text, term) for term in group_terms):
                additions.extend(group_terms)

        if not additions:
            return normalized_text

        seen: set[str] = set()
        tokens: list[str] = []
        for token in f"{normalized_text} {' '.join(additions)}".split():
            if token in seen:
                continue
            seen.add(token)
            tokens.append(token)
        return " ".join(tokens)

    @classmethod
    def expand_query_variants(
        cls,
        normalized_query: str,
        *,
        max_variants: int = 12,
    ) -> list[str]:
        if not normalized_query:
            return []

        variants: set[str] = {normalized_query}
        for canonical, synonyms in cls.DOMAIN_SYNONYM_GROUPS.items():
            group_terms = (canonical, *synonyms)
            matched_terms = [
                term for term in group_terms if cls.contains_phrase(normalized_query, term)
            ]
            if not matched_terms:
                continue

            variants.update(group_terms)
            for matched_term in matched_terms:
                for replacement in group_terms:
                    variants.add(
                        cls.replace_phrase(normalized_query, matched_term, replacement)
                    )

        return sorted(variants, key=lambda item: (-len(item), item))[:max_variants]
