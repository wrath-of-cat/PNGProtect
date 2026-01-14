'''use 
python -m uvicorn app.main:app --reload
to run the server'''

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import watermark, verify, metadata, detection, registry
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI(
    title="PNGProtect API",
    description="Invisible image watermarking with AI-based tampering detection.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(watermark.router, prefix="/watermark", tags=["Watermark"])
app.include_router(verify.router, prefix="/verify", tags=["Verify"])
app.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])
app.include_router(detection.router, prefix="/detect", tags=["Detection"])
app.include_router(registry.router, prefix="/registry", tags=["Registry"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "API running"}
