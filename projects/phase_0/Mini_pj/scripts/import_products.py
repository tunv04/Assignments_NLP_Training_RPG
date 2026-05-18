from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.repositories.product_repository import ProductRepository
from app.services.text_normalizer import TextNormalizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "chiaki_products.json"
ROOT_INPUT_PATH = PROJECT_ROOT / "chiaki_products.json"

NAME_KEYS = ("name", "title", "product_name")
URL_KEYS = ("url", "link", "product_url")
DESCRIPTION_KEYS = ("description", "desc", "detail", "content", "summary")
CATEGORY_KEYS = ("category", "category_name", "cate", "breadcrumb")
PRICE_KEYS = ("price", "sale_price", "current_price", "price_text")
SOURCE_KEYS = ("source", "site", "domain")
COMMENT_KEYS = ("comments", "reviews", "feedbacks", "review")
COMMENT_CONTENT_KEYS = ("content", "comment", "text", "review", "body", "message")

COMMENT_COLUMN_MIGRATIONS = {
    "author": "VARCHAR",
    "rating": "INTEGER",
    "date": "VARCHAR",
}


def resolve_input_path() -> Path:
    if DEFAULT_INPUT_PATH.exists():
        return DEFAULT_INPUT_PATH
    if ROOT_INPUT_PATH.exists():
        return ROOT_INPUT_PATH
    raise FileNotFoundError(
        "Cannot find input file. Expected data/chiaki_products.json "
        "or chiaki_products.json in the project root."
    )


def read_records(path: Path) -> list[dict[str, Any]]:
    raw_text = path.read_text(encoding="utf-8-sig").strip()
    if not raw_text:
        return []

    try:
        data = json.loads(raw_text)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        if isinstance(item, dict):
            records.append(item)
    return records


def pick_value(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value

    lower_record = {str(key).lower(): value for key, value in record.items()}
    for key in keys:
        value = lower_record.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def value_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = [value_to_text(item) for item in value]
        return " ".join(part for part in parts if part).strip()
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def value_to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return int(float(value))
        except ValueError:
            return None
    return None


def extract_comments(record: dict[str, Any]) -> list[Any]:
    raw_comments = pick_value(record, COMMENT_KEYS)
    if raw_comments is None:
        return []

    if isinstance(raw_comments, dict):
        for nested_key in ("items", "data", "comments", "reviews"):
            nested_value = raw_comments.get(nested_key)
            if isinstance(nested_value, list):
                raw_comments = nested_value
                break
        else:
            return [raw_comments]

    if isinstance(raw_comments, list):
        return raw_comments

    return [raw_comments]


def build_product_payload(record: dict[str, Any]) -> dict[str, str | None]:
    name = value_to_text(pick_value(record, NAME_KEYS))
    description = value_to_text(pick_value(record, DESCRIPTION_KEYS))

    return {
        "name": name,
        "normalized_name": TextNormalizer.normalize_for_index(name),
        "url": value_to_text(pick_value(record, URL_KEYS)) or None,
        "description": description or None,
        "normalized_description": TextNormalizer.normalize_for_index(description),
        "category": value_to_text(pick_value(record, CATEGORY_KEYS)) or None,
        "price": value_to_text(pick_value(record, PRICE_KEYS)) or None,
        "source": value_to_text(pick_value(record, SOURCE_KEYS)) or "chiaki.vn",
    }


def build_comment_payloads(record: dict[str, Any]) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for comment_data in extract_comments(record):
        if isinstance(comment_data, dict):
            author_data = comment_data.get("author")
            rating_data = comment_data.get("rating")
            content_data = comment_data.get("content")
            date_data = comment_data.get("date")

            content = value_to_text(
                content_data
                if content_data is not None
                else pick_value(comment_data, COMMENT_CONTENT_KEYS)
            )
            author = value_to_text(author_data) or None
            rating = value_to_int(rating_data)
            date = value_to_text(date_data) or None
        else:
            content = value_to_text(comment_data)
            author = None
            rating = None
            date = None

        if not content.strip():
            continue

        normalized_content = TextNormalizer.normalize_for_index(content)
        payloads.append(
            {
                "author": author,
                "rating": rating,
                "content": content,
                "normalized_content": normalized_content,
                "date": date,
            }
        )
    return payloads


def ensure_comment_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("comments"):
        return

    if engine.dialect.name == "postgresql":
        statements = [
            "ALTER TABLE comments ADD COLUMN IF NOT EXISTS author VARCHAR",
            "ALTER TABLE comments ADD COLUMN IF NOT EXISTS rating INTEGER",
            "ALTER TABLE comments ADD COLUMN IF NOT EXISTS date VARCHAR",
        ]
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("comments")
    }
    with engine.begin() as connection:
        for column_name, column_type in COMMENT_COLUMN_MIGRATIONS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE comments ADD COLUMN {column_name} {column_type}")
                )


def import_products(input_path: Path | None = None) -> tuple[int, int, int]:
    path = input_path or resolve_input_path()
    records = read_records(path)

    inserted = 0
    updated = 0
    skipped = 0

    Base.metadata.create_all(bind=engine)
    ensure_comment_columns()

    with SessionLocal() as db:
        repository = ProductRepository(db)
        try:
            for record in records:
                product_data = build_product_payload(record)
                if not product_data["name"]:
                    skipped += 1
                    continue

                comments = build_comment_payloads(record)
                _, created = repository.upsert_product(product_data, comments)
                db.flush()

                if created:
                    inserted += 1
                else:
                    updated += 1

            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    return inserted, updated, skipped


def main() -> None:
    input_path = resolve_input_path()
    inserted, updated, skipped = import_products(input_path)
    print(f"Input file: {input_path}")
    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
