from __future__ import annotations

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import PROJECT_ROOT, settings


def _resolve_sqlite_url(database_url: str) -> str:
    if not database_url.startswith("sqlite:///"):
        return database_url

    raw_path = database_url.replace("sqlite:///", "", 1)
    if raw_path == ":memory:":
        return database_url

    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def _connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


SQLALCHEMY_DATABASE_URL = _resolve_sqlite_url(settings.database_url)

engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=_connect_args(SQLALCHEMY_DATABASE_URL),
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
