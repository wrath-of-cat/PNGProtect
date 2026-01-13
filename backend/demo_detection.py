"""
Watermark Removal Detection - Example Usage

Demonstrates how to use the detection system for analyzing images.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
from app.services.detection import WatermarkRemovalDetector
from app.services.forensics import ForensicsAnalyzer
from app.services.ml_classifier import FeatureExtractor


def demo_full_analysis(image_path: str, model_path: str = None):
    """
    Run complete detection analysis on an image.
    
    Args:
        image_path: Path to image file
        model_path: Optional path to trained ML model
    """
    print("=" * 60)
    print("WATERMARK REMOVAL DETECTION - FULL ANALYSIS")
    print("=" * 60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    print(f"\nImage: {image_path}")
    print(f"Dimensions: {image.shape}")
    
    # Initialize detector
    detector = WatermarkRemovalDetector(model_path)
    
    # Run analysis
    print("\nRunning detection analysis...")
    report = detector.analyze_image(image)
    
    # Display results
    print(f"\n{'─' * 60}")
    print("DETECTION RESULTS")
    print(f"{'─' * 60}")
    
    print(f"\nOverall Tampering Confidence: {report.overall_tampering_confidence:.1f}%")
    print(f"Confidence Level: {report.confidence_level}")
    print(f"Watermark Likely Removed: {'YES' if report.likely_removed else 'NO'}")
    
    print(f"\n{'─' * 60}")
    print("DETECTED TECHNIQUES")
    print(f"{'─' * 60}")
    
    if report.detected_techniques:
        for i, technique in enumerate(report.detected_techniques, 1):
            print(f"{i}. {technique}")
    else:
        print("No tampering techniques detected")
    
    print(f"\n{'─' * 60}")
    print("FORENSIC ANALYSIS")
    print(f"{'─' * 60}")
    
    print("\nArtifact Detections:")
    for artifact_type, artifact_data in report.forensic_artifacts.items():
        confidence = artifact_data['confidence']
        detected = artifact_data['detected']
        status = "✓" if detected else "✗"
        print(f"\n{status} {artifact_data['artifact_type']}")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"  Description: {artifact_data['description']}")
    
    print(f"\n{'─' * 60}")
    print("MACHINE LEARNING ANALYSIS")
    print(f"{'─' * 60}")
    
    print(f"\nML Tampering Probability: {report.ml_tampering_probability:.3f}")
    print(f"ML Confidence Score: {report.ml_confidence:.1f}%")
    
    print(f"\n{'─' * 60}")
    print("FORENSIC EXPLANATION")
    print(f"{'─' * 60}")
    
    print(f"\n{report.forensic_explanation}")
    
    print(f"\n{'─' * 60}")
    print("TECHNICAL SUMMARY")
    print(f"{'─' * 60}")
    
    print(f"\n{report.technical_summary}")


def demo_forensics_only(image_path: str):
    """
    Run forensics-only analysis (no ML, faster).
    
    Args:
        image_path: Path to image file
    """
    print("=" * 60)
    print("WATERMARK REMOVAL DETECTION - FORENSICS ONLY")
    print("=" * 60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    print(f"\nImage: {image_path}")
    print(f"Dimensions: {image.shape}")
    
    # Run forensics
    print("\nRunning forensics analysis...")
    analyzer = ForensicsAnalyzer(image)
    results = analyzer.analyze_all()
    
    print(f"\n{'─' * 60}")
    print("FORENSIC RESULTS")
    print(f"{'─' * 60}")
    
    for artifact_type, result in results.items():
        print(f"\n{result.artifact_type}")
        print(f"  Confidence: {result.confidence:.1f}%")
        print(f"  Description: {result.description}")
        print(f"  Affected Regions: {result.affected_region_percentage:.1f}%")
    
    # Overall confidence
    overall = analyzer.get_summary_confidence(results)
    print(f"\n{'─' * 60}")
    print(f"Overall Forensics Confidence: {overall:.1f}%")


def demo_feature_extraction(image_path: str):
    """
    Extract and display all features from image.
    
    Args:
        image_path: Path to image file
    """
    print("=" * 60)
    print("FEATURE EXTRACTION DEMO")
    print("=" * 60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    print(f"\nImage: {image_path}")
    print(f"Dimensions: {image.shape}")
    
    # Extract features
    print("\nExtracting features...")
    extractor = FeatureExtractor(image)
    features = extractor.extract_all_features()
    
    print(f"\n{'─' * 60}")
    print(f"EXTRACTED FEATURES ({len(features)} total)")
    print(f"{'─' * 60}")
    
    # Group by type
    statistical = extractor.extract_statistical_features()
    gradient = extractor.extract_gradient_features()
    frequency = extractor.extract_frequency_features()
    lbp = extractor.extract_local_binary_pattern_features()
    block = extractor.extract_block_consistency_features()
    
    print(f"\nSTATISTICAL FEATURES ({len(statistical)}):")
    for key, value in sorted(statistical.items()):
        print(f"  {key:30s}: {value:12.6f}")
    
    print(f"\nGRADIENT FEATURES ({len(gradient)}):")
    for key, value in sorted(gradient.items()):
        print(f"  {key:30s}: {value:12.6f}")
    
    print(f"\nFREQUENCY FEATURES ({len(frequency)}):")
    for key, value in sorted(frequency.items()):
        print(f"  {key:30s}: {value:12.6f}")
    
    print(f"\nTEXTURE FEATURES ({len(lbp)}):")
    for key, value in sorted(lbp.items()):
        print(f"  {key:30s}: {value:12.6f}")
    
    print(f"\nBLOCK CONSISTENCY FEATURES ({len(block)}):")
    for key, value in sorted(block.items()):
        print(f"  {key:30s}: {value:12.6f}")


def demo_batch_analysis(image_dir: str, model_path: str = None):
    """
    Run detection on all images in a directory.
    
    Args:
        image_dir: Directory containing images
        model_path: Optional path to trained model
    """
    print("=" * 60)
    print("BATCH ANALYSIS")
    print("=" * 60)
    
    from pathlib import Path
    
    image_dir = Path(image_dir)
    detector = WatermarkRemovalDetector(model_path)
    
    results_summary = []
    
    # Process all images
    for image_path in sorted(image_dir.glob('*.*')):
        if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp']:
            continue
        
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            
            report = detector.analyze_image(image)
            
            result = {
                'file': image_path.name,
                'confidence': report.overall_tampering_confidence,
                'likely_removed': report.likely_removed,
                'techniques': len(report.detected_techniques)
            }
            
            results_summary.append(result)
            
            status = "⚠" if report.likely_removed else "✓"
            print(f"{status} {image_path.name:40s} {report.overall_tampering_confidence:6.1f}% ({report.confidence_level})")
        
        except Exception as e:
            print(f"✗ {image_path.name:40s} Error: {e}")
    
    # Summary
    if results_summary:
        print(f"\n{'─' * 60}")
        print("SUMMARY")
        print(f"{'─' * 60}")
        
        print(f"\nTotal images: {len(results_summary)}")
        
        suspicious = sum(1 for r in results_summary if r['likely_removed'])
        print(f"Suspicious (likely tampered): {suspicious}")
        
        avg_confidence = np.mean([r['confidence'] for r in results_summary])
        print(f"Average confidence: {avg_confidence:.1f}%")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Watermark Detection Demo")
    parser.add_argument('image', nargs='?', help='Image file path')
    parser.add_argument('--mode', choices=['full', 'forensics', 'features', 'batch'],
                       default='full', help='Analysis mode')
    parser.add_argument('--model', help='Path to trained ML model')
    
    args = parser.parse_args()
    
    if not args.image:
        print("Usage: python demo.py <image> [--mode full|forensics|features|batch] [--model MODEL_PATH]")
        print("\nExamples:")
        print("  python demo.py test.jpg                           # Full analysis")
        print("  python demo.py test.jpg --mode forensics          # Forensics only (faster)")
        print("  python demo.py test.jpg --mode features           # Feature extraction")
        print("  python demo.py image_dir --mode batch             # Batch analysis")
        print("  python demo.py test.jpg --model model.pkl         # Use trained model")
        sys.exit(1)
    
    if args.mode == 'full':
        demo_full_analysis(args.image, args.model)
    elif args.mode == 'forensics':
        demo_forensics_only(args.image)
    elif args.mode == 'features':
        demo_feature_extraction(args.image)
    elif args.mode == 'batch':
        demo_batch_analysis(args.image, args.model)
