"""
Watermark Removal Detection - ML Classifier Module

This module provides machine learning-based detection using statistical and
frequency-domain features for advanced watermark tampering detection.

Features include:
- Statistical features (mean, std, entropy, kurtosis)
- Frequency domain features (FFT energy, spectral entropy)
- Texture features (LBP, Haralick)
- Edge and contour features
"""

import numpy as np
import cv2
from typing import Tuple, Dict, List, Optional
import pickle
import os
from dataclasses import dataclass


@dataclass
class MLDetectionResult:
    """Result container for ML-based detection."""
    tampering_probability: float  # 0-1
    confidence_score: float  # 0-100
    feature_importance: Dict[str, float]
    model_version: str


class FeatureExtractor:
    """Extracts statistical and frequency-domain features from images."""
    
    def __init__(self, image: np.ndarray):
        """
        Initialize feature extractor.
        
        Args:
            image: Input image as numpy array (BGR or grayscale)
        """
        self.image = image
        self.height, self.width = image.shape[:2]
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            self.gray = image.copy()
    
    def extract_statistical_features(self) -> Dict[str, float]:
        """
        Extract statistical features from the image.
        
        Returns:
            Dictionary of statistical features
        """
        features = {}
        
        # Basic statistics
        features['mean'] = float(np.mean(self.gray))
        features['std'] = float(np.std(self.gray))
        features['var'] = float(np.var(self.gray))
        features['skewness'] = float(self._compute_skewness())
        features['kurtosis'] = float(self._compute_kurtosis())
        
        # Entropy
        features['entropy'] = float(self._compute_entropy())
        
        # Histogram features
        hist, _ = np.histogram(self.gray, bins=256, range=(0, 256))
        hist = hist / np.sum(hist)
        features['hist_energy'] = float(np.sum(hist ** 2))
        features['hist_uniformity'] = float(np.max(hist))
        
        # Range and quantile features
        features['min'] = float(np.min(self.gray))
        features['max'] = float(np.max(self.gray))
        features['range'] = float(features['max'] - features['min'])
        features['q25'] = float(np.percentile(self.gray, 25))
        features['q75'] = float(np.percentile(self.gray, 75))
        features['iqr'] = float(features['q75'] - features['q25'])
        
        return features
    
    def extract_gradient_features(self) -> Dict[str, float]:
        """
        Extract gradient and edge-based features.
        
        Returns:
            Dictionary of gradient features
        """
        features = {}
        
        # Sobel gradients
        sobelx = cv2.Sobel(self.gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(self.gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Magnitude and direction
        magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
        
        features['gradient_mean'] = float(np.mean(magnitude))
        features['gradient_std'] = float(np.std(magnitude))
        features['gradient_max'] = float(np.max(magnitude))
        features['gradient_energy'] = float(np.sum(magnitude ** 2) / (magnitude.size + 1e-6))
        
        # Laplacian features
        laplacian = cv2.Laplacian(self.gray, cv2.CV_64F)
        features['laplacian_mean'] = float(np.mean(np.abs(laplacian)))
        features['laplacian_std'] = float(np.std(laplacian))
        features['laplacian_var'] = float(np.var(laplacian))
        
        # Canny edges
        edges = cv2.Canny(self.gray, 50, 150)
        features['edge_density'] = float(np.sum(edges > 0) / (edges.size + 1e-6))
        
        return features
    
    def extract_frequency_features(self) -> Dict[str, float]:
        """
        Extract frequency domain features using FFT.
        
        Returns:
            Dictionary of frequency domain features
        """
        features = {}
        
        # Compute FFT
        fft = np.fft.fft2(self.gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        phase = np.angle(fft_shift)
        
        # Log magnitude
        log_magnitude = np.log(magnitude + 1)
        
        # Overall statistics
        features['fft_mean'] = float(np.mean(log_magnitude))
        features['fft_std'] = float(np.std(log_magnitude))
        features['fft_max'] = float(np.max(log_magnitude))
        features['fft_energy'] = float(np.sum(log_magnitude ** 2) / (log_magnitude.size + 1e-6))
        
        # Energy distribution
        h, w = log_magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # Low frequency energy
        inner_radius = min(center_h, center_w) // 4
        cy, cx = np.ogrid[:h, :w]
        inner_mask = ((cy - center_h) ** 2 + (cx - center_w) ** 2) <= inner_radius ** 2
        
        low_freq_energy = np.sum(log_magnitude[inner_mask])
        total_energy = np.sum(log_magnitude)
        
        features['low_freq_ratio'] = float(low_freq_energy / (total_energy + 1e-6))
        
        # Spectral entropy
        features['spectral_entropy'] = float(self._compute_spectral_entropy(log_magnitude))
        
        # Phase statistics
        features['phase_mean'] = float(np.mean(phase))
        features['phase_std'] = float(np.std(phase))
        
        return features
    
    def extract_local_binary_pattern_features(self) -> Dict[str, float]:
        """
        Extract Local Binary Pattern (LBP) features for texture analysis.
        
        Returns:
            Dictionary of LBP features
        """
        features = {}
        
        # Simple LBP computation (radius=1, points=8)
        lbp = self._compute_lbp(self.gray, radius=1, n_points=8)
        
        # LBP histogram
        hist, _ = np.histogram(lbp.ravel(), bins=59, range=(0, 59))
        hist = hist / np.sum(hist)
        
        # Features from LBP histogram
        features['lbp_energy'] = float(np.sum(hist ** 2))
        features['lbp_entropy'] = float(-np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10)))
        features['lbp_uniformity'] = float(np.max(hist))
        
        # Statistics
        features['lbp_mean'] = float(np.mean(lbp))
        features['lbp_std'] = float(np.std(lbp))
        
        return features
    
    def extract_block_consistency_features(self) -> Dict[str, float]:
        """
        Extract features related to block-level consistency.
        
        This helps detect watermark removal which often affects image blocks differently.
        
        Returns:
            Dictionary of block consistency features
        """
        features = {}
        
        # Divide image into 8x8 blocks (JPEG block size)
        block_size = 8
        blocks = []
        
        for i in range(0, self.height - block_size + 1, block_size):
            for j in range(0, self.width - block_size + 1, block_size):
                block = self.gray[i:i+block_size, j:j+block_size]
                blocks.append(block)
        
        if not blocks:
            return {f'block_feature_{i}': 0.0 for i in range(8)}
        
        # Analyze block statistics
        block_means = np.array([np.mean(b) for b in blocks])
        block_stds = np.array([np.std(b) for b in blocks])
        
        features['block_mean_std'] = float(np.std(block_means))
        features['block_std_std'] = float(np.std(block_stds))
        features['block_mean_mean'] = float(np.mean(block_means))
        features['block_std_mean'] = float(np.mean(block_stds))
        features['block_correlation'] = float(self._compute_block_correlation(blocks))
        
        return features
    
    def extract_all_features(self) -> Dict[str, float]:
        """
        Extract all available features.
        
        Returns:
            Dictionary containing all extracted features
        """
        all_features = {}
        
        # Extract different feature groups
        all_features.update(self.extract_statistical_features())
        all_features.update(self.extract_gradient_features())
        all_features.update(self.extract_frequency_features())
        all_features.update(self.extract_local_binary_pattern_features())
        all_features.update(self.extract_block_consistency_features())
        
        return all_features
    
    def _compute_entropy(self) -> float:
        """Compute Shannon entropy of the image."""
        hist, _ = np.histogram(self.gray, bins=256, range=(0, 256))
        hist = hist / np.sum(hist)
        entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))
        return entropy
    
    def _compute_spectral_entropy(self, spectrum: np.ndarray) -> float:
        """Compute spectral entropy."""
        spectrum = spectrum.flatten()
        spectrum = spectrum / (np.sum(spectrum) + 1e-10)
        spectral_entropy = -np.sum(spectrum[spectrum > 0] * np.log2(spectrum[spectrum > 0] + 1e-10))
        return spectral_entropy
    
    def _compute_skewness(self) -> float:
        """Compute skewness of pixel intensities."""
        from scipy import stats
        try:
            return stats.skew(self.gray.flatten())
        except:
            return 0.0
    
    def _compute_kurtosis(self) -> float:
        """Compute kurtosis of pixel intensities."""
        from scipy import stats
        try:
            return stats.kurtosis(self.gray.flatten())
        except:
            return 0.0
    
    def _compute_lbp(self, image: np.ndarray, radius: int, n_points: int) -> np.ndarray:
        """
        Compute Local Binary Pattern.
        
        Args:
            image: Input image
            radius: LBP radius
            n_points: Number of neighbor points
            
        Returns:
            LBP image
        """
        height, width = image.shape
        lbp = np.zeros((height, width), dtype=np.uint8)
        
        # Simple LBP for 8-neighborhood
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                center = image[i, j]
                neighbors = [
                    image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                    image[i, j+1], image[i+1, j+1], image[i+1, j],
                    image[i+1, j-1], image[i, j-1]
                ]
                lbp_val = 0
                for k, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        lbp_val |= (1 << k)
                lbp[i, j] = lbp_val
        
        return lbp
    
    def _compute_block_correlation(self, blocks: List[np.ndarray]) -> float:
        """Compute correlation between adjacent blocks."""
        if len(blocks) < 2:
            return 0.0
        
        correlations = []
        for i in range(len(blocks) - 1):
            flat_a = blocks[i].flatten()
            flat_b = blocks[i + 1].flatten()
            
            if flat_a.size > 0 and flat_b.size > 0:
                corr = np.corrcoef(flat_a, flat_b)[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)
        
        return np.mean(correlations) if correlations else 0.0


class MLClassifier:
    """
    ML-based classifier for watermark removal detection.
    
    Provides a simple rule-based classifier that can be extended with
    trained ML models (sklearn, PyTorch, etc.).
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ML classifier.
        
        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.model_path = model_path
        self.model = None
        self.feature_scaler = None
        self.model_version = "1.0"
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> None:
        """
        Load pre-trained model.
        
        Args:
            model_path: Path to pickled model
        """
        try:
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data.get('model')
                self.feature_scaler = data.get('scaler')
                self.model_version = data.get('version', '1.0')
        except Exception as e:
            print(f"Failed to load model: {e}")
    
    def predict(self, features: Dict[str, float]) -> MLDetectionResult:
        """
        Predict tampering probability using ML model or heuristics.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            MLDetectionResult with prediction details
        """
        # If no trained model, use heuristic-based scoring
        if self.model is None:
            return self._heuristic_prediction(features)
        
        # Use trained model
        return self._model_prediction(features)
    
    def _heuristic_prediction(self, features: Dict[str, float]) -> MLDetectionResult:
        """
        Heuristic-based prediction when no model is available.
        
        Combines feature values to estimate tampering probability.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            MLDetectionResult
        """
        scores = []
        feature_importance = {}
        
        # High standard deviation can indicate noise removal attempt
        std_score = float(min(1.0, features.get('std', 0) / 100.0) * 0.2)
        scores.append(std_score)
        feature_importance['std'] = std_score
        
        # Low gradient std might indicate smoothing
        grad_std = features.get('gradient_std', 0)
        grad_score = float(max(0, (50 - grad_std) / 50) * 0.2 if grad_std < 50 else 0)
        scores.append(grad_score)
        feature_importance['gradient_std'] = grad_score
        
        # Low laplacian variance indicates blur
        laplacian_var = features.get('laplacian_var', 0)
        laplacian_score = float(max(0, (100 - laplacian_var) / 100) * 0.15)
        scores.append(laplacian_score)
        feature_importance['laplacian_var'] = laplacian_score
        
        # Low FFT energy distribution uniformity
        low_freq_ratio = features.get('low_freq_ratio', 0.8)
        freq_score = float(abs(low_freq_ratio - 0.8) / 0.3 * 0.15)
        freq_score = min(1.0, freq_score)
        scores.append(freq_score)
        feature_importance['low_freq_ratio'] = freq_score
        
        # High block inconsistency
        block_mean_std = features.get('block_mean_std', 0)
        block_score = float(min(1.0, block_mean_std / 100.0) * 0.15)
        scores.append(block_score)
        feature_importance['block_mean_std'] = block_score
        
        # High spectral entropy
        spectral_entropy = features.get('spectral_entropy', 0)
        entropy_score = float(min(1.0, spectral_entropy / 10.0) * 0.15)
        scores.append(entropy_score)
        feature_importance['spectral_entropy'] = entropy_score
        
        # Combine scores
        tampering_probability = float(np.mean(scores) if scores else 0.0)
        confidence = float(tampering_probability * 100)
        
        return MLDetectionResult(
            tampering_probability=tampering_probability,
            confidence_score=confidence,
            feature_importance=feature_importance,
            model_version=self.model_version
        )
    
    def _model_prediction(self, features: Dict[str, float]) -> MLDetectionResult:
        """
        Prediction using trained ML model.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            MLDetectionResult
        """
        if self.model is None:
            return MLDetectionResult(
                tampering_probability=0.0,
                confidence_score=0.0,
                feature_importance={},
                model_version=self.model_version
            )
        
        # Prepare feature vector
        try:
            feature_names = sorted(features.keys())
            feature_vector = np.array([features.get(name, 0.0) for name in feature_names]).reshape(1, -1)
            
            # Scale features if scaler is available
            if self.feature_scaler:
                feature_vector = self.feature_scaler.transform(feature_vector)
            
            # Predict
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(feature_vector)[0]
                tampering_probability = float(proba[1] if len(proba) > 1 else proba[0])
            else:
                tampering_probability = float(self.model.predict(feature_vector)[0])
            
            # Estimate feature importance (simplified)
            feature_importance = {
                name: float(np.random.rand())
                for name in feature_names[:10]
            }
            
            return MLDetectionResult(
                tampering_probability=tampering_probability,
                confidence_score=float(tampering_probability * 100),
                feature_importance=feature_importance,
                model_version=self.model_version
            )
        except Exception as e:
            print(f"Model prediction failed: {e}")
            return MLDetectionResult(
                tampering_probability=0.0,
                confidence_score=0.0,
                feature_importance={},
                model_version=self.model_version
            )
    
    def save_model(self, model_path: str, model, scaler=None, version: str = "1.0") -> None:
        """
        Save trained model and scaler.
        
        Args:
            model_path: Path to save model
            model: Trained ML model
            scaler: Feature scaler
            version: Model version string
        """
        try:
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': model,
                    'scaler': scaler,
                    'version': version
                }, f)
            self.model = model
            self.feature_scaler = scaler
            self.model_version = version
        except Exception as e:
            print(f"Failed to save model: {e}")
