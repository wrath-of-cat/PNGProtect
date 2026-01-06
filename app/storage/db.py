from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


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
  Simple in-memory storage for watermark metadata.
  Suitable for hackathon/demo purposes; swap with SQLite later if needed.
  """

  _instance: "WatermarkStore | None" = None

  def __init__(self) -> None:
      self.records_by_id: Dict[str, WatermarkRecord] = {}
      self.records_by_hash: Dict[str, WatermarkRecord] = {}

  @classmethod
  def get_instance(cls) -> "WatermarkStore":
      if cls._instance is None:
          cls._instance = WatermarkStore()
      return cls._instance

  def save_record(
      self,
      watermark_id: str,
      image_hash: str,
      owner_id: str,
      strength: int,
      total_bits: int,
  ) -> None:
      rec = WatermarkRecord(
          watermark_id=watermark_id,
          image_hash=image_hash,
          owner_id=owner_id,
          strength=strength,
          total_bits=total_bits,
          timestamp=datetime.utcnow(),
      )
      self.records_by_id[watermark_id] = rec
      self.records_by_hash[image_hash] = rec

  def get_by_image_hash(self, image_hash: str) -> Optional[WatermarkRecord]:
      return self.records_by_hash.get(image_hash)

  def get_by_watermark_id(self, watermark_id: str) -> Optional[WatermarkRecord]:
      return self.records_by_id.get(watermark_id)

  def get_by_owner_and_hash_prefix(
      self, extracted_text: str, image_hash: str
  ) -> Optional[WatermarkRecord]:
      """
      Very simple lookup heuristic:
      - First see if we have an exact image hash match, then trust that.
      - If not, try to match on owner_id substring vs extracted_text.
      """
      rec = self.records_by_hash.get(image_hash)
      if rec:
          # check if extracted_text contains owner_id (common for handles/IDs)
          if rec.owner_id in extracted_text or extracted_text in rec.owner_id:
              return rec

      # fallback: find any record whose ownerId is inside extracted text
      for r in self.records_by_id.values():
          if r.owner_id in extracted_text or extracted_text in r.owner_id:
              return r
      return None
