"""
Watermark Removal Detection - Forensics Analysis Module

This module provides rule-based detection for common watermark tampering techniques:
- Blur detection (Laplacian variance)
- Noise inconsistency analysis
- Compression artifact detection
- Edge density anomalies
- Frequency domain analysis (FFT-based)
"""

import numpy as np
import cv2
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class ArtifactDetectionResult:
    """Result container for artifact detection."""
    artifact_type: str
    confidence: float  # 0-100
    description: str
    affected_region_percentage: float


class ForensicsAnalyzer:
    """Rule-based forensics analyzer for watermark tampering detection."""
    
    def __init__(self, image: np.ndarray):
        """
        Initialize forensics analyzer.
        
        Args:
            image: Input image as numpy array (BGR or grayscale)
        """
        self.image = image
        self.height, self.width = image.shape[:2]
        
        # Convert to grayscale if color image
        if len(image.shape) == 3:
            self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            self.gray = image.copy()
    
    def detect_blur(self, threshold: float = 100.0) -> ArtifactDetectionResult:
        """
        Detect blur using Laplacian variance method.
        
        Lower variance indicates more blur, which suggests watermark removal attempt.
        
        Args:
            threshold: Laplacian variance threshold (lower = more blur detected)
            
        Returns:
            ArtifactDetectionResult with blur detection details
        """
        # Compute Laplacian and its variance
        laplacian = cv2.Laplacian(self.gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize to 0-100 confidence scale
        # Lower variance = higher blur confidence
        blur_confidence = max(0, min(100, 100 - (variance / threshold * 100)))
        
        return ArtifactDetectionResult(
            artifact_type="Blur",
            confidence=blur_confidence,
            description=f"Laplacian variance: {variance:.2f}. Low variance indicates blur (watermark removal technique).",
            affected_region_percentage=100.0
        )
    
    def detect_noise_inconsistency(self) -> ArtifactDetectionResult:
        """
        Detect noise inconsistency between regions.
        
        Watermark removal often leaves inconsistent noise patterns or smoothed regions.
        Compares local noise levels across the image.
        
        Returns:
            ArtifactDetectionResult with noise inconsistency details
        """
        # Divide image into 4x4 grid and analyze noise in each region
        grid_size = 4
        tile_height = self.height // grid_size
        tile_width = self.width // grid_size
        
        noise_levels = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                y_start = i * tile_height
                y_end = (i + 1) * tile_height if i < grid_size - 1 else self.height
                x_start = j * tile_width
                x_end = (j + 1) * tile_width if j < grid_size - 1 else self.width
                
                tile = self.gray[y_start:y_end, x_start:x_end]
                
                # Compute local noise as standard deviation
                if tile.size > 0:
                    noise = np.std(tile)
                    noise_levels.append(noise)
        
        noise_levels = np.array(noise_levels)
        
        if len(noise_levels) == 0:
            return ArtifactDetectionResult(
                artifact_type="Noise Inconsistency",
                confidence=0.0,
                description="Unable to analyze noise.",
                affected_region_percentage=0.0
            )
        
        # Compute coefficient of variation (std dev of noise levels)
        mean_noise = np.mean(noise_levels)
        noise_variation = np.std(noise_levels) / (mean_noise + 1e-6)
        
        # High variation indicates inconsistent noise (tampering indicator)
        noise_confidence = min(100, max(0, noise_variation * 30))
        
        # Identify which regions have unusual noise
        threshold = mean_noise + 1.5 * np.std(noise_levels)
        anomalous_regions = np.sum(noise_levels < mean_noise - 1.5 * np.std(noise_levels))
        affected_percentage = (anomalous_regions / len(noise_levels)) * 100
        
        return ArtifactDetectionResult(
            artifact_type="Noise Inconsistency",
            confidence=noise_confidence,
            description=f"Noise variation: {noise_variation:.4f}. Anomalous regions detected in {affected_percentage:.1f}% of image tiles.",
            affected_region_percentage=affected_percentage
        )
    
    def detect_compression_artifacts(self) -> ArtifactDetectionResult:
        """
        Detect recompression artifacts and JPEG blocking.
        
        Watermark removal may involve re-encoding, leaving compression artifacts.
        
        Returns:
            ArtifactDetectionResult with compression artifact details
        """
        # Apply high-pass filter to highlight block boundaries
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]], dtype=np.float32)
        
        filtered = cv2.filter2D(self.gray, cv2.CV_32F, kernel)
        filtered_abs = np.abs(filtered)
        
        # Block size for JPEG is 8x8
        block_size = 8
        
        # Detect periodic patterns at block boundaries
        blockiness = 0.0
        boundary_samples = []
        
        for i in range(block_size, self.height, block_size):
            for j in range(block_size, self.width, block_size):
                # Sample edges between blocks
                if i < self.height and j < self.width:
                    val = filtered_abs[i, j]
                    boundary_samples.append(val)
        
        if boundary_samples:
            boundary_mean = np.mean(boundary_samples)
            blockiness = boundary_mean
        
        # Normalize to 0-100 confidence
        compression_confidence = min(100, max(0, (blockiness / 20) * 100))
        
        return ArtifactDetectionResult(
            artifact_type="Recompression",
            confidence=compression_confidence,
            description=f"Block boundary detection: {blockiness:.2f}. JPEG-like compression patterns detected.",
            affected_region_percentage=100.0
        )
    
    def detect_edge_anomalies(self) -> ArtifactDetectionResult:
        """
        Detect edge density anomalies that may indicate tampering.
        
        Watermark removal can create unnatural edge patterns or edge smoothing.
        
        Returns:
            ArtifactDetectionResult with edge anomaly details
        """
        # Compute Canny edges
        edges = cv2.Canny(self.gray, 50, 150)
        
        # Divide into grid and analyze edge density
        grid_size = 4
        tile_height = self.height // grid_size
        tile_width = self.width // grid_size
        
        edge_densities = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                y_start = i * tile_height
                y_end = (i + 1) * tile_height if i < grid_size - 1 else self.height
                x_start = j * tile_width
                x_end = (j + 1) * tile_width if j < grid_size - 1 else self.width
                
                tile = edges[y_start:y_end, x_start:x_end]
                density = np.sum(tile > 0) / (tile.size + 1e-6)
                edge_densities.append(density)
        
        edge_densities = np.array(edge_densities)
        
        # Detect anomalies (regions with significantly different edge density)
        mean_density = np.mean(edge_densities)
        std_density = np.std(edge_densities)
        
        anomalies = np.sum(np.abs(edge_densities - mean_density) > 2.5 * std_density)
        anomaly_percentage = (anomalies / len(edge_densities)) * 100
        
        # Confidence based on anomaly detection
        edge_confidence = min(100, max(0, anomaly_percentage * 1.5))
        
        return ArtifactDetectionResult(
            artifact_type="Edge Anomalies",
            confidence=edge_confidence,
            description=f"Edge density variation: {std_density:.4f}. Anomalous edge patterns in {anomaly_percentage:.1f}% of regions.",
            affected_region_percentage=anomaly_percentage
        )
    
    def detect_frequency_anomalies(self) -> ArtifactDetectionResult:
        """
        Detect frequency domain anomalies using FFT.
        
        Watermark removal techniques may leave frequency-domain signatures.
        
        Returns:
            ArtifactDetectionResult with frequency anomaly details
        """
        # Compute FFT
        fft = np.fft.fft2(self.gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        # Log scale for better visualization
        log_magnitude = np.log(magnitude + 1)
        
        # Normalize
        log_magnitude = (log_magnitude - log_magnitude.min()) / (log_magnitude.max() - log_magnitude.min() + 1e-6)
        
        # Analyze energy distribution
        # Expected pattern for natural images: energy concentrated in low frequencies
        h, w = log_magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # Energy in central region (low frequency)
        inner_radius = min(center_h, center_w) // 4
        cy, cx = np.ogrid[:h, :w]
        inner_mask = ((cy - center_h) ** 2 + (cx - center_w) ** 2) <= inner_radius ** 2
        
        low_freq_energy = np.sum(log_magnitude[inner_mask])
        total_energy = np.sum(log_magnitude)
        
        low_freq_ratio = low_freq_energy / (total_energy + 1e-6)
        
        # Anomaly: unexpected energy distribution
        # Natural images typically have 70-90% energy in low frequencies
        expected_low_freq = 0.80
        freq_anomaly = abs(low_freq_ratio - expected_low_freq)
        
        # Confidence: how much the distribution deviates from expected
        freq_confidence = min(100, max(0, freq_anomaly * 200))
        
        return ArtifactDetectionResult(
            artifact_type="Frequency Anomaly",
            confidence=freq_confidence,
            description=f"Low-frequency energy ratio: {low_freq_ratio:.3f}. Unexpected frequency distribution detected.",
            affected_region_percentage=100.0
        )
    
    def analyze_all(self) -> Dict[str, ArtifactDetectionResult]:
        """
        Run all forensic checks.
        
        Returns:
            Dictionary mapping artifact types to detection results
        """
        results = {}
        
        results['blur'] = self.detect_blur()
        results['noise_inconsistency'] = self.detect_noise_inconsistency()
        results['recompression'] = self.detect_compression_artifacts()
        results['edge_anomalies'] = self.detect_edge_anomalies()
        results['frequency_anomaly'] = self.detect_frequency_anomalies()
        
        return results
    
    def get_summary_confidence(self, results: Dict[str, ArtifactDetectionResult]) -> float:
        """
        Compute overall tampering confidence from individual detections.
        
        Args:
            results: Dictionary of detection results
            
        Returns:
            Overall confidence score (0-100)
        """
        if not results:
            return 0.0
        
        # Weighted combination of detections
        weights = {
            'blur': 0.25,
            'noise_inconsistency': 0.25,
            'recompression': 0.20,
            'edge_anomalies': 0.15,
            'frequency_anomaly': 0.15
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for artifact_type, result in results.items():
            weight = weights.get(artifact_type, 0.1)
            weighted_sum += result.confidence * weight
            total_weight += weight
        
        overall_confidence = weighted_sum / (total_weight + 1e-6)
        
        return min(100, max(0, overall_confidence))
