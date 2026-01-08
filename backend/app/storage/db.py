from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import sqlite3


DB_PATH = Path(__file__).with_name("watermarks.db")


@dataclass
class WatermarkRecord:
    watermark_id: str
    image_hash: str
    owner_id: str
    strength: int
    total_bits: int
    timestamp: datetime


class WatermarkStore:
    """
    SQLite-backed storage for watermark metadata.
    Persisted in watermarks.db, survives server restarts.
    """

    _instance: "WatermarkStore | None" = None

    def __init__(self) -> None:
        # Use check_same_thread=False so FastAPI threads can share the connection.
        # For a real app, use a connection per request or a pool via SQLAlchemy. [web:117][web:121]
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS watermarks (
                watermark_id TEXT PRIMARY KEY,
                image_hash   TEXT NOT NULL,
                owner_id     TEXT NOT NULL,
                strength     INTEGER NOT NULL,
                total_bits   INTEGER NOT NULL,
                created_at   TEXT NOT NULL
            );
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_watermarks_image_hash ON watermarks (image_hash);"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_watermarks_owner_id ON watermarks (owner_id);"
        )
        self.conn.commit()

    @classmethod
    def get_instance(cls) -> "WatermarkStore":
        if cls._instance is None:
            cls._instance = WatermarkStore()
        return cls._instance

    # ---------- CRUD helpers ----------

    def save_record(
        self,
        watermark_id: str,
        image_hash: str,
        owner_id: str,
        strength: int,
        total_bits: int,
    ) -> None:
        created_at = datetime.utcnow().isoformat()
        self.conn.execute(
            """
            INSERT OR REPLACE INTO watermarks
            (watermark_id, image_hash, owner_id, strength, total_bits, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (watermark_id, image_hash, owner_id, strength, total_bits, created_at),
        )
        self.conn.commit()

    def _row_to_record(self, row: sqlite3.Row | None) -> Optional[WatermarkRecord]:
        if row is None:
            return None
        return WatermarkRecord(
            watermark_id=row["watermark_id"],
            image_hash=row["image_hash"],
            owner_id=row["owner_id"],
            strength=row["strength"],
            total_bits=row["total_bits"],
            timestamp=datetime.fromisoformat(row["created_at"]),
        )

    def get_by_image_hash(self, image_hash: str) -> Optional[WatermarkRecord]:
        cur = self.conn.execute(
            "SELECT * FROM watermarks WHERE image_hash = ? LIMIT 1;", (image_hash,)
        )
        row = cur.fetchone()
        return self._row_to_record(row)

    def get_by_watermark_id(self, watermark_id: str) -> Optional[WatermarkRecord]:
        cur = self.conn.execute(
            "SELECT * FROM watermarks WHERE watermark_id = ? LIMIT 1;", (watermark_id,)
        )
        row = cur.fetchone()
        return self._row_to_record(row)

    def get_by_owner_and_hash_prefix(
        self, extracted_text: str, image_hash: str
    ) -> Optional[WatermarkRecord]:
        """
        Same heuristic as before, but using SQL instead of dicts:
        1. Try exact hash match and check owner_id vs extracted_text.
        2. Fallback: any row where owner_id LIKE '%%extracted_text%%'.
        """

        # 1) Exact hash match first
        cur = self.conn.execute(
            "SELECT * FROM watermarks WHERE image_hash = ? LIMIT 1;", (image_hash,)
        )
        row = cur.fetchone()
        rec = self._row_to_record(row)
        if rec:
            if rec.owner_id in extracted_text or extracted_text in rec.owner_id:
                return rec

        # 2) Fallback search on owner_id
        like_pattern = f"%{extracted_text}%"
        cur = self.conn.execute(
            "SELECT * FROM watermarks WHERE owner_id LIKE ? LIMIT 1;",
            (like_pattern,),
        )
        row = cur.fetchone()
        return self._row_to_record(row)
