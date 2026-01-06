from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.hashing import sha256_bytes
from app.services.watermarking import (
    extract_watermark_lsb,
    load_image_from_bytes,
)
from app.storage.db import WatermarkStore
from app.models.schemas import VerifyResponse, PublicVerifyResponse

router = APIRouter()
store = WatermarkStore.get_instance()

def validate_image_upload(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload a PNG or JPEG.")

@router.post("", response_model=VerifyResponse, summary="Verify image watermark")
async def verify_image(file: UploadFile = File(...)):
    validate_image_upload(file)
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty payload.")

    image_hash = sha256_bytes(raw_bytes)
    image = load_image_from_bytes(raw_bytes)

    # Extraction
    extracted_text, match_ratio = extract_watermark_lsb(image)

    # DB Match
    record = store.get_by_owner_and_hash_prefix(extracted_text, image_hash)

    watermark_found = record is not None
    owner_id = record.owner_id if record else None

    # Your Tamper/Confidence Logic
    if watermark_found:
        if match_ratio > 0.9:
            confidence, tamper_status = int(90 + (match_ratio - 0.9) * 100), "intact"
        elif match_ratio > 0.7:
            confidence, tamper_status = int(60 + (match_ratio - 0.7) * 100), "modified"
        else:
            confidence, tamper_status = int(40 + match_ratio * 100), "modified"
    else:
        if match_ratio > 0.4:
            confidence, tamper_status = int(20 + match_ratio * 80), "modified"
        else:
            confidence, tamper_status = int(match_ratio * 40), "no watermark"

    return VerifyResponse(
        watermark_found=watermark_found,
        owner_id=owner_id,
        confidence=max(0, min(100, confidence)),
        tamper_status=tamper_status,
        extracted_text=extracted_text,
        match_ratio=match_ratio,
    )

@router.get("/public/{watermark_id}", response_model=PublicVerifyResponse)
async def public_lookup(watermark_id: str):
    record = store.get_by_watermark_id(watermark_id)
    if not record:
        raise HTTPException(status_code=404, detail="ID not found.")

    return PublicVerifyResponse(
        watermark_id=watermark_id,
        owner_id=record.owner_id,
        image_hash=record.image_hash,
        strength=record.strength,
        created_at=record.timestamp,
    )