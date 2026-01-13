"""
Watermark Removal Detection API Routes

Endpoints for watermark removal/tampering detection using the hybrid
forensics + ML detection system.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import traceback

from app.services.detection import WatermarkRemovalDetector

router = APIRouter()


@router.post("/detect", summary="Detect watermark removal/tampering")
async def detect_watermark_removal(file: UploadFile = File(...)):
    """
    Analyze image for watermark removal or tampering.
    
    Uses hybrid forensics + ML analysis to detect:
    - Blur and smoothing artifacts
    - Noise inconsistencies
    - Compression artifacts
    - Edge anomalies
    - Frequency domain anomalies
    
    Args:
        file: Image file to analyze (PNG, JPEG, etc.)
        
    Returns:
        Detection report with:
        - Overall tampering confidence (0-100%)
        - Detected artifact types
        - ML probability score
        - Forensic explanations
        - Technical analysis
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Upload a valid image file (PNG, JPEG, etc.).")
        
        # Read image
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file payload.")
        
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to decode image. Ensure it's a valid image file.")
        
        # Initialize detector
        detector = WatermarkRemovalDetector()
        
        # Analyze image
        report = detector.analyze_image(image)
        
        # Convert report to dictionary
        report_dict = detector.get_report_dict(report)
        
        # Convert tuples to lists for JSON
        if isinstance(report_dict.get('image_dimensions'), tuple):
            report_dict['image_dimensions'] = list(report_dict['image_dimensions'])
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "detection_report": report_dict
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Detection error: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Detection analysis failed: {str(e)}"
        )


@router.post("/forensics-only", summary="Run forensics analysis only")
async def forensics_only(file: UploadFile = File(...)):
    """
    Run only forensics-based detection (no ML).
    
    Faster analysis focusing on rule-based artifact detection:
    - Blur (Laplacian variance)
    - Noise inconsistency
    - Compression artifacts
    - Edge anomalies
    - Frequency anomalies
    
    Args:
        file: Image file to analyze
        
    Returns:
        Forensic analysis results with artifact detections
    """
    try:
        # Validate and read file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Upload a valid image file.")
        
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file payload.")
        
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to decode image.")
        
        # Run forensics only
        from app.services.forensics import ForensicsAnalyzer
        
        analyzer = ForensicsAnalyzer(image)
        forensic_results = analyzer.analyze_all()
        
        # Format results
        formatted_results = {}
        for artifact_type, result in forensic_results.items():
            formatted_results[artifact_type] = {
                'artifact_type': result.artifact_type,
                'confidence': round(result.confidence, 2),
                'description': result.description,
                'affected_region_percentage': round(result.affected_region_percentage, 2)
            }
        
        # Compute overall confidence
        overall_confidence = analyzer.get_summary_confidence(forensic_results)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "overall_confidence": round(overall_confidence, 2),
                "artifacts": formatted_results,
                "image_dimensions": [image.shape[1], image.shape[0]]
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Forensics error: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Forensics analysis failed: {str(e)}"
        )


@router.post("/extract-features", summary="Extract analysis features")
async def extract_features(file: UploadFile = File(...)):
    """
    Extract statistical and frequency-domain features from image.
    
    Useful for training custom ML models or debugging analysis.
    
    Features include:
    - Statistical (mean, std, entropy, kurtosis)
    - Gradient/Edge (Sobel, Laplacian, Canny)
    - Frequency domain (FFT, spectral entropy)
    - Texture (LBP)
    - Block consistency
    
    Args:
        file: Image file to analyze
        
    Returns:
        Dictionary of extracted features
    """
    try:
        # Validate and read file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Upload a valid image file.")
        
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file payload.")
        
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to decode image.")
        
        # Extract features
        from app.services.ml_classifier import FeatureExtractor
        
        extractor = FeatureExtractor(image)
        features = extractor.extract_all_features()
        
        # Round for JSON serialization
        features_rounded = {k: round(v, 6) for k, v in features.items()}
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "features": features_rounded,
                "feature_count": len(features),
                "image_dimensions": [image.shape[1], image.shape[0]]
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Feature extraction error: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Feature extraction failed: {str(e)}"
        )
