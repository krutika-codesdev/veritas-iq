from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.models.schema import Product


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "veritasiq.db"


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db() -> None:
    """Create the VeritasIQ SQLite database and tables."""

    with _get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                manufacturer TEXT,
                brand TEXT,
                model_number TEXT,
                health_score REAL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()


def save_product(
    product: Product,
    health_score: float | None = None,
) -> int:
    """Persist a canonical Product and return its database ID."""

    init_db()

    now = datetime.now(timezone.utc).isoformat()

    payload = json.dumps(
        product.model_dump(mode="json"),
        ensure_ascii=False,
    )

    with _get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO products (
                product_name,
                manufacturer,
                brand,
                model_number,
                health_score,
                payload_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product.product_name,
                product.manufacturer,
                product.brand,
                product.model_number,
                health_score,
                payload,
                now,
                now,
            ),
        )

        connection.commit()

        return int(cursor.lastrowid)


def get_product(product_id: int) -> Product | None:
    """Retrieve a Product by database ID."""

    init_db()

    with _get_connection() as connection:
        row = connection.execute(
            """
            SELECT payload_json
            FROM products
            WHERE id = ?
            """,
            (product_id,),
        ).fetchone()

    if row is None:
        return None

    payload = json.loads(row["payload_json"])

    return Product.model_validate(payload)


def list_products() -> list[dict]:
    """Return persisted product summaries."""

    init_db()

    with _get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                product_name,
                manufacturer,
                brand,
                model_number,
                health_score,
                created_at,
                updated_at
            FROM products
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]