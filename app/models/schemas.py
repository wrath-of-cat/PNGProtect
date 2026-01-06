from datetime import datetime
from pydantic import BaseModel


class WatermarkResponse(BaseModel):
  """
  Logical response schema; actual binary image is returned as HTTP body, while
  metadata (watermark ID, hash) is available via headers.
  """
  # Kept minimal; Swagger will still show this schema.
  # Fields will reflect headers for convenience.
  # For this demo we don't add fields here explicitly.


class BatchItem(BaseModel):
  filename: str
  watermark_id: str
  image_hash: str


class BatchWatermarkResponse(BaseModel):
  count: int
  items: list[BatchItem]


class VerifyResponse(BaseModel):
  watermark_found: bool
  owner_id: str | None
  confidence: int
  tamper_status: str
  extracted_text: str
  match_ratio: float


class PublicVerifyResponse(BaseModel):
  watermark_id: str
  owner_id: str
  image_hash: str
  strength: int
  created_at: datetime
