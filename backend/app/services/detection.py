"""
Watermark Removal Detection - Main Detection Orchestrator

This module combines rule-based forensics analysis with ML-based classification
to provide comprehensive watermark removal detection.

Includes:
- Hybrid detection combining forensics and ML
- Detailed forensic explanations
- Artifact type classification
- Confidence scoring and reporting
"""

import numpy as np
import cv2
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from app.services.forensics import ForensicsAnalyzer, ArtifactDetectionResult
from app.services.ml_classifier import FeatureExtractor, MLClassifier


class TamperingConfidence(Enum):
    """Tampering confidence levels."""
    VERY_LOW = "Very Low (0-20%)"
    LOW = "Low (20-40%)"
    MEDIUM = "Medium (40-60%)"
    HIGH = "High (60-80%)"
    VERY_HIGH = "Very High (80-100%)"


@dataclass
class WatermarkRemovalDetectionReport:
    """Complete watermark removal detection report."""
    overall_tampering_confidence: float  # 0-100
    confidence_level: str  # Very Low, Low, Medium, High, Very High
    likely_removed: bool  # Watermark likely removed based on confidence
    
    # Forensic analysis results
    forensic_artifacts: Dict[str, Dict]  # artifact_type -> artifact details
    
    # ML-based prediction
    ml_tampering_probability: float  # 0-1
    ml_confidence: float  # 0-100
    
    # Detected techniques
    detected_techniques: List[str]  # e.g., ["Blur", "Recompression"]
    
    # Detailed explanation
    forensic_explanation: str
    technical_summary: str
    
    # Metadata
    image_dimensions: Tuple[int, int]
    analysis_timestamp: str


class WatermarkRemovalDetector:
    """
    Comprehensive watermark removal detection system.
    
    Combines rule-based forensics analysis with ML-based classification
    for robust detection of watermark tampering and removal.
    """
    
    def __init__(self, ml_model_path: Optional[str] = None):
        """
        Initialize detector.
        
        Args:
            ml_model_path: Optional path to pre-trained ML model
        """
        self.ml_classifier = MLClassifier(ml_model_path)
        self.forensics_analyzer = None
        self.feature_extractor = None
    
    def analyze_image(self, image: np.ndarray) -> WatermarkRemovalDetectionReport:
        """
        Analyze image for watermark removal/tampering.
        
        Args:
            image: Input image as numpy array (BGR or grayscale)
            
        Returns:
            Comprehensive detection report
        """
        import datetime
        
        # Prepare image
        if image is None or image.size == 0:
            raise ValueError("Invalid image")
        
        # Initialize analyzers
        self.forensics_analyzer = ForensicsAnalyzer(image)
        self.feature_extractor = FeatureExtractor(image)
        
        # Run forensic analysis
        forensic_results = self.forensics_analyzer.analyze_all()
        forensic_artifacts = self._format_forensic_results(forensic_results)
        
        # Run ML analysis
        features = self.feature_extractor.extract_all_features()
        ml_result = self.ml_classifier.predict(features)
        
        # Compute overall confidence
        overall_confidence = self._compute_overall_confidence(
            forensic_results,
            ml_result
        )
        
        # Detect techniques
        detected_techniques = self._identify_techniques(
            forensic_results,
            ml_result
        )
        
        # Generate explanations
        forensic_explanation = self._generate_forensic_explanation(
            forensic_results,
            detected_techniques
        )
        
        technical_summary = self._generate_technical_summary(
            overall_confidence,
            ml_result,
            forensic_results
        )
        
        # Determine if watermark likely removed
        likely_removed = overall_confidence > 60
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(overall_confidence)
        
        # Create report
        report = WatermarkRemovalDetectionReport(
            overall_tampering_confidence=overall_confidence,
            confidence_level=confidence_level,
            likely_removed=likely_removed,
            forensic_artifacts=forensic_artifacts,
            ml_tampering_probability=ml_result.tampering_probability,
            ml_confidence=ml_result.confidence_score,
            detected_techniques=detected_techniques,
            forensic_explanation=forensic_explanation,
            technical_summary=technical_summary,
            image_dimensions=(image.shape[1], image.shape[0]),
            analysis_timestamp=datetime.datetime.now().isoformat()
        )
        
        return report
    
    def analyze_image_bytes(self, image_bytes: bytes) -> WatermarkRemovalDetectionReport:
        """
        Analyze image from byte data.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Comprehensive detection report
        """
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        return self.analyze_image(image)
    
    def _format_forensic_results(
        self, 
        results: Dict[str, ArtifactDetectionResult]
    ) -> Dict[str, Dict]:
        """
        Format forensic results for the report.
        
        Args:
            results: Raw forensic detection results
            
        Returns:
            Formatted results dictionary
        """
        formatted = {}
        
        for artifact_type, result in results.items():
            formatted[artifact_type] = {
                'artifact_type': result.artifact_type,
                'confidence': round(result.confidence, 2),
                'description': result.description,
                'affected_region_percentage': round(result.affected_region_percentage, 2),
                'detected': result.confidence > 30  # Detection threshold
            }
        
        return formatted
    
    def _compute_overall_confidence(
        self,
        forensic_results: Dict[str, ArtifactDetectionResult],
        ml_result
    ) -> float:
        """
        Compute overall tampering confidence.
        
        Combines forensic and ML results.
        
        Args:
            forensic_results: Forensic detection results
            ml_result: ML classification result
            
        Returns:
            Overall confidence (0-100)
        """
        # Forensic confidence (weighted average)
        forensic_confidence = self.forensics_analyzer.get_summary_confidence(forensic_results)
        
        # ML confidence
        ml_confidence = ml_result.confidence_score
        
        # Weighted combination
        # 60% forensic, 40% ML
        overall = (forensic_confidence * 0.6) + (ml_confidence * 0.4)
        
        return min(100, max(0, overall))
    
    def _identify_techniques(
        self,
        forensic_results: Dict[str, ArtifactDetectionResult],
        ml_result
    ) -> List[str]:
        """
        Identify specific watermark removal techniques.
        
        Args:
            forensic_results: Forensic detection results
            ml_result: ML classification result
            
        Returns:
            List of detected technique names
        """
        techniques = []
        detection_threshold = 30  # Confidence threshold
        
        # Check forensic detections
        for artifact_type, result in forensic_results.items():
            if result.confidence > detection_threshold:
                techniques.append(result.artifact_type)
        
        # Add context from ML
        if ml_result.tampering_probability > 0.5:
            if len(techniques) == 0:
                techniques.append("Unidentified Tampering")
        
        return techniques
    
    def _generate_forensic_explanation(
        self,
        forensic_results: Dict[str, ArtifactDetectionResult],
        detected_techniques: List[str]
    ) -> str:
        """
        Generate human-readable forensic explanation.
        
        Args:
            forensic_results: Forensic detection results
            detected_techniques: List of detected techniques
            
        Returns:
            Forensic explanation string
        """
        explanation_parts = []
        
        if not detected_techniques:
            explanation_parts.append(
                "No significant watermark removal artifacts detected. "
                "The image appears to have maintained its integrity."
            )
        else:
            explanation_parts.append(
                f"Analysis detected {len(detected_techniques)} potential watermark removal technique(s):"
            )
            explanation_parts.append("")
            
            for technique in detected_techniques:
                # Find corresponding result
                result = None
                for key, res in forensic_results.items():
                    if res.artifact_type == technique:
                        result = res
                        break
                
                if result:
                    explanation_parts.append(f"• {technique} (Confidence: {result.confidence:.1f}%)")
                    explanation_parts.append(f"  {result.description}")
                    explanation_parts.append("")
        
        return "\n".join(explanation_parts)
    
    def _generate_technical_summary(
        self,
        overall_confidence: float,
        ml_result,
        forensic_results: Dict[str, ArtifactDetectionResult]
    ) -> str:
        """
        Generate technical summary of the analysis.
        
        Args:
            overall_confidence: Overall tampering confidence
            ml_result: ML classification result
            forensic_results: Forensic detection results
            
        Returns:
            Technical summary string
        """
        summary = f"""
WATERMARK REMOVAL DETECTION ANALYSIS
{'='*50}

OVERALL ASSESSMENT:
- Tampering Confidence: {overall_confidence:.1f}%
- Watermark Removal Likely: {"YES" if overall_confidence > 60 else "NO"}

FORENSIC ANALYSIS:
"""
        
        for artifact_type, result in forensic_results.items():
            summary += f"\n- {result.artifact_type}: {result.confidence:.1f}% confidence"
        
        summary += f"""

MACHINE LEARNING ANALYSIS:
- ML Tampering Probability: {ml_result.tampering_probability:.3f}
- ML Confidence Score: {ml_result.confidence_score:.1f}%
- Model Version: {ml_result.model_version}

TECHNICAL INSIGHTS:
"""
        
        high_confidence_artifacts = [
            result for result in forensic_results.values()
            if result.confidence > 60
        ]
        
        if high_confidence_artifacts:
            summary += f"\nDetected high-confidence artifacts ({len(high_confidence_artifacts)}):\n"
            for artifact in high_confidence_artifacts:
                summary += f"  - {artifact.artifact_type}: {artifact.confidence:.1f}%\n"
        else:
            summary += "\nNo high-confidence artifacts detected.\n"
        
        summary += "\n" + "="*50
        
        return summary
    
    def _get_confidence_level(self, confidence: float) -> str:
        """
        Convert numerical confidence to level descriptor.
        
        Args:
            confidence: Confidence score (0-100)
            
        Returns:
            Confidence level string
        """
        if confidence < 20:
            return TamperingConfidence.VERY_LOW.value
        elif confidence < 40:
            return TamperingConfidence.LOW.value
        elif confidence < 60:
            return TamperingConfidence.MEDIUM.value
        elif confidence < 80:
            return TamperingConfidence.HIGH.value
        else:
            return TamperingConfidence.VERY_HIGH.value
    
    def get_report_dict(self, report: WatermarkRemovalDetectionReport) -> Dict:
        """
        Convert report to dictionary for JSON serialization.
        
        Args:
            report: Detection report
            
        Returns:
            Dictionary representation
        """
        report_dict = asdict(report)
        
        # Ensure all values are JSON serializable
        report_dict['overall_tampering_confidence'] = float(report_dict['overall_tampering_confidence'])
        report_dict['ml_tampering_probability'] = float(report_dict['ml_tampering_probability'])
        report_dict['ml_confidence'] = float(report_dict['ml_confidence'])
        
        # Convert bool to string for JSON
        report_dict['likely_removed'] = bool(report_dict['likely_removed'])
        
        # Handle forensic artifacts
        if report_dict.get('forensic_artifacts'):
            for artifact_type, artifact_data in report_dict['forensic_artifacts'].items():
                if isinstance(artifact_data, dict):
                    artifact_data['confidence'] = float(artifact_data['confidence'])
                    artifact_data['affected_region_percentage'] = float(artifact_data['affected_region_percentage'])
                    artifact_data['detected'] = bool(artifact_data.get('detected', False))
        
        # Handle image dimensions tuple
        if isinstance(report_dict.get('image_dimensions'), tuple):
            report_dict['image_dimensions'] = list(report_dict['image_dimensions'])
        
        return report_dict
    
    def get_report_json(self, report: WatermarkRemovalDetectionReport) -> str:
        """
        Convert report to JSON string.
        
        Args:
            report: Detection report
            
        Returns:
            JSON string
        """
        import json
        
        report_dict = self.get_report_dict(report)
        
        # Convert tuples to lists for JSON serialization
        if isinstance(report_dict.get('image_dimensions'), tuple):
            report_dict['image_dimensions'] = list(report_dict['image_dimensions'])
        
        return json.dumps(report_dict, indent=2)
