from __future__ import annotations

from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

from app.db.base import Base
from app.db.session import SQLALCHEMY_DATABASE_URL, engine


def masked_database_url() -> str:
    return make_url(SQLALCHEMY_DATABASE_URL).render_as_string(hide_password=True)


def main() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        print(f"Cannot connect to database: {masked_database_url()}")
        print("Check DATABASE_URL, PostgreSQL username/password, host, port, and database name.")
        raise SystemExit(1) from exc

    print(f"Tables created successfully: {masked_database_url()}")


if __name__ == "__main__":
    main()
