"""
Watermark Removal Detection - Training & Testing Utilities

Script for training ML models, evaluating detection performance,
and testing the detection system.
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import json
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.detection import WatermarkRemovalDetector
from app.services.ml_classifier import FeatureExtractor, MLClassifier
from app.services.forensics import ForensicsAnalyzer


class DetectionTrainer:
    """Train and evaluate the detection system."""
    
    @staticmethod
    def extract_dataset_features(
        clean_dir: str,
        attacked_dir: str,
        output_file: str = 'features.json'
    ) -> Dict[str, List]:
        """
        Extract features from training dataset.
        
        Args:
            clean_dir: Directory containing clean/non-tampered images
            attacked_dir: Directory containing watermark-removed/attacked images
            output_file: File to save extracted features
            
        Returns:
            Dictionary with clean and attacked features
        """
        dataset = {
            'clean': [],
            'attacked': []
        }
        
        # Process clean images
        print(f"Processing clean images from {clean_dir}...")
        clean_path = Path(clean_dir)
        for img_file in clean_path.glob('*.*'):
            if img_file.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp']:
                continue
            
            try:
                image = cv2.imread(str(img_file))
                if image is None:
                    continue
                
                extractor = FeatureExtractor(image)
                features = extractor.extract_all_features()
                features['file'] = str(img_file)
                features['label'] = 0  # Clean
                dataset['clean'].append(features)
                
                print(f"  ✓ {img_file.name}")
            except Exception as e:
                print(f"  ✗ {img_file.name}: {e}")
        
        # Process attacked images
        print(f"\nProcessing attacked images from {attacked_dir}...")
        attacked_path = Path(attacked_dir)
        for img_file in attacked_path.glob('*.*'):
            if img_file.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp']:
                continue
            
            try:
                image = cv2.imread(str(img_file))
                if image is None:
                    continue
                
                extractor = FeatureExtractor(image)
                features = extractor.extract_all_features()
                features['file'] = str(img_file)
                features['label'] = 1  # Attacked
                dataset['attacked'].append(features)
                
                print(f"  ✓ {img_file.name}")
            except Exception as e:
                print(f"  ✗ {img_file.name}: {e}")
        
        # Save features
        print(f"\nSaving features to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Dataset Summary:")
        print(f"  Clean images: {len(dataset['clean'])}")
        print(f"  Attacked images: {len(dataset['attacked'])}")
        
        return dataset
    
    @staticmethod
    def train_sklearn_model(
        features_file: str,
        model_output: str = 'watermark_detection_model.pkl'
    ) -> Tuple:
        """
        Train a scikit-learn classifier using extracted features.
        
        Args:
            features_file: JSON file with extracted features
            model_output: Path to save trained model
            
        Returns:
            Tuple of (model, scaler)
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, 
                f1_score, roc_auc_score
            )
        except ImportError:
            print("scikit-learn not installed. Install with: pip install scikit-learn")
            return None, None
        
        print(f"Loading features from {features_file}...")
        with open(features_file, 'r') as f:
            dataset = json.load(f)
        
        # Prepare data
        all_samples = dataset['clean'] + dataset['attacked']
        
        # Extract features and labels
        feature_keys = None
        X_list = []
        y_list = []
        
        for sample in all_samples:
            if feature_keys is None:
                feature_keys = sorted([k for k in sample.keys() if k not in ['file', 'label']])
            
            x = [sample[k] for k in feature_keys]
            X_list.append(x)
            y_list.append(sample.get('label', 0))
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        print(f"Features shape: {X.shape}")
        print(f"Labels distribution: {np.bincount(y)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        print("\nScaling features...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        print("Training Random Forest classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        print("\nEvaluating model...")
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\nModel Performance:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  ROC-AUC:   {roc_auc:.4f}")
        
        # Feature importance
        print(f"\nTop 10 Important Features:")
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]
        for idx, feature_idx in enumerate(indices):
            print(f"  {idx+1}. {feature_keys[feature_idx]}: {importances[feature_idx]:.4f}")
        
        # Save model
        print(f"\nSaving model to {model_output}...")
        classifier = MLClassifier()
        classifier.save_model(model_output, model, scaler, version="2.0")
        print(f"Model saved successfully!")
        
        return model, scaler
    
    @staticmethod
    def evaluate_detection_accuracy(
        clean_dir: str,
        attacked_dir: str,
        model_path: str = None
    ) -> Dict:
        """
        Evaluate detection accuracy on a test dataset.
        
        Args:
            clean_dir: Directory with clean images
            attacked_dir: Directory with attacked images
            model_path: Optional path to trained model
            
        Returns:
            Dictionary with evaluation results
        """
        detector = WatermarkRemovalDetector(model_path)
        
        results = {
            'clean': {'correct': 0, 'total': 0, 'scores': []},
            'attacked': {'correct': 0, 'total': 0, 'scores': []}
        }
        
        # Test clean images
        print("Evaluating detection on clean images...")
        clean_path = Path(clean_dir)
        for img_file in clean_path.glob('*.*'):
            if img_file.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp']:
                continue
            
            try:
                image = cv2.imread(str(img_file))
                if image is None:
                    continue
                
                report = detector.analyze_image(image)
                score = report.overall_tampering_confidence
                
                # Clean image should have low confidence
                is_correct = score < 50
                
                results['clean']['total'] += 1
                results['clean']['scores'].append(score)
                if is_correct:
                    results['clean']['correct'] += 1
                
                status = "✓" if is_correct else "✗"
                print(f"  {status} {img_file.name}: {score:.1f}%")
            except Exception as e:
                print(f"  ✗ {img_file.name}: {e}")
        
        # Test attacked images
        print("\nEvaluating detection on attacked images...")
        attacked_path = Path(attacked_dir)
        for img_file in attacked_path.glob('*.*'):
            if img_file.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp']:
                continue
            
            try:
                image = cv2.imread(str(img_file))
                if image is None:
                    continue
                
                report = detector.analyze_image(image)
                score = report.overall_tampering_confidence
                
                # Attacked image should have high confidence
                is_correct = score > 50
                
                results['attacked']['total'] += 1
                results['attacked']['scores'].append(score)
                if is_correct:
                    results['attacked']['correct'] += 1
                
                status = "✓" if is_correct else "✗"
                print(f"  {status} {img_file.name}: {score:.1f}%")
            except Exception as e:
                print(f"  ✗ {img_file.name}: {e}")
        
        # Compute metrics
        if results['clean']['total'] > 0:
            clean_accuracy = results['clean']['correct'] / results['clean']['total']
        else:
            clean_accuracy = 0
        
        if results['attacked']['total'] > 0:
            attacked_accuracy = results['attacked']['correct'] / results['attacked']['total']
        else:
            attacked_accuracy = 0
        
        total_correct = results['clean']['correct'] + results['attacked']['correct']
        total_samples = results['clean']['total'] + results['attacked']['total']
        
        overall_accuracy = total_correct / total_samples if total_samples > 0 else 0
        
        print(f"\nEvaluation Results:")
        print(f"  Clean Accuracy:   {clean_accuracy:.1%} ({results['clean']['correct']}/{results['clean']['total']})")
        print(f"  Attacked Accuracy: {attacked_accuracy:.1%} ({results['attacked']['correct']}/{results['attacked']['total']})")
        print(f"  Overall Accuracy: {overall_accuracy:.1%} ({total_correct}/{total_samples})")
        
        if results['clean']['scores']:
            print(f"\n  Clean scores - Mean: {np.mean(results['clean']['scores']):.1f}%, Std: {np.std(results['clean']['scores']):.1f}%")
        
        if results['attacked']['scores']:
            print(f"  Attacked scores - Mean: {np.mean(results['attacked']['scores']):.1f}%, Std: {np.std(results['attacked']['scores']):.1f}%")
        
        return {
            'clean_accuracy': float(clean_accuracy),
            'attacked_accuracy': float(attacked_accuracy),
            'overall_accuracy': float(overall_accuracy),
            'results': results
        }


def main():
    """Main entry point for training/testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Watermark Detection Training & Testing")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Extract features command
    extract_cmd = subparsers.add_parser('extract', help='Extract features from images')
    extract_cmd.add_argument('--clean', required=True, help='Directory with clean images')
    extract_cmd.add_argument('--attacked', required=True, help='Directory with attacked images')
    extract_cmd.add_argument('--output', default='features.json', help='Output features file')
    
    # Train model command
    train_cmd = subparsers.add_parser('train', help='Train ML model')
    train_cmd.add_argument('--features', required=True, help='Features JSON file')
    train_cmd.add_argument('--output', default='watermark_detection_model.pkl', help='Output model file')
    
    # Evaluate command
    eval_cmd = subparsers.add_parser('evaluate', help='Evaluate detection accuracy')
    eval_cmd.add_argument('--clean', required=True, help='Directory with clean images')
    eval_cmd.add_argument('--attacked', required=True, help='Directory with attacked images')
    eval_cmd.add_argument('--model', help='Optional trained model path')
    
    # Test single image
    test_cmd = subparsers.add_parser('test', help='Test single image')
    test_cmd.add_argument('--image', required=True, help='Image file path')
    test_cmd.add_argument('--model', help='Optional trained model path')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        DetectionTrainer.extract_dataset_features(
            args.clean, args.attacked, args.output
        )
    
    elif args.command == 'train':
        DetectionTrainer.train_sklearn_model(args.features, args.output)
    
    elif args.command == 'evaluate':
        DetectionTrainer.evaluate_detection_accuracy(
            args.clean, args.attacked, args.model
        )
    
    elif args.command == 'test':
        detector = WatermarkRemovalDetector(args.model)
        image = cv2.imread(args.image)
        
        if image is None:
            print(f"Failed to load image: {args.image}")
            return
        
        print(f"Analyzing {args.image}...\n")
        report = detector.analyze_image(image)
        
        print(f"Overall Tampering Confidence: {report.overall_tampering_confidence:.1f}%")
        print(f"Confidence Level: {report.confidence_level}")
        print(f"Watermark Likely Removed: {report.likely_removed}")
        print(f"\nDetected Techniques: {', '.join(report.detected_techniques)}")
        print(f"\n{report.forensic_explanation}")
        print(f"\n{report.technical_summary}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
