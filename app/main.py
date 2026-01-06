from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import watermark, verify

app = FastAPI(
    title="Invisible Image Watermarking API",
    description="LSB watermarking backend.",
    version="0.1.0",
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

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "API running"}