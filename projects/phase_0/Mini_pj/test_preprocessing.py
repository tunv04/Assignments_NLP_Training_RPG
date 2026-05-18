
from app.services.text_normalizer import TextNormalizer


def main() -> None:
    cases = {
        "Viên uống Bổ Gan!!!": "bo gan",
        "<b>Vitamin Đ</b>": "vitamin d",
        "SP omega3 tốt quá": "omega 3",
        "vitmin cho bé": "vitamin be",
        "thuốc táo-bón": "tao bon",
        "Tăng sức đề kháng": "tang suc de khang",
    }

    for raw_text, expected in cases.items():
        actual = TextNormalizer.normalize_for_query(raw_text)
        assert actual == expected, f"{raw_text!r}: expected {expected!r}, got {actual!r}"

    variants = TextNormalizer.expand_query_variants(
        TextNormalizer.normalize_for_query("probiotic")
    )
    assert "men vi sinh" in variants

    expanded = TextNormalizer.expand_with_synonyms(
        TextNormalizer.normalize_for_query("omega3")
    )
    assert "dau" in expanded and "ca" in expanded

    print("Text preprocessing tests passed.")


if __name__ == "__main__":
    main()
