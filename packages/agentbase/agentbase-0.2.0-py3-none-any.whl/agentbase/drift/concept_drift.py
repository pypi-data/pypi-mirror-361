"""
Concept Drift Detection - Track changes in data distributions over time.

This module provides comprehensive drift detection capabilities for monitoring
changes in data patterns, model performance, and system behavior over time.
"""

import numpy as np
import threading
import time
from collections import deque, defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from abc import ABC, abstractmethod


class DriftType(Enum):
    """Types of concept drift."""
    GRADUAL = "gradual"
    SUDDEN = "sudden"
    INCREMENTAL = "incremental"
    RECURRING = "recurring"
    VIRTUAL = "virtual"


class DriftSeverity(Enum):
    """Severity levels of drift."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriftAlert:
    """
    Alert generated when drift is detected.
    """
    timestamp: float
    drift_type: DriftType
    severity: DriftSeverity
    feature_name: str
    drift_score: float
    threshold: float
    description: str
    statistical_test: str
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["drift_type"] = self.drift_type.value
        data["severity"] = self.severity.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DriftAlert':
        """Create from dictionary."""
        data["drift_type"] = DriftType(data["drift_type"])
        data["severity"] = DriftSeverity(data["severity"])
        return cls(**data)


@dataclass
class DataSnapshot:
    """
    Snapshot of data statistics at a point in time.
    """
    timestamp: float
    feature_name: str
    mean: float
    std: float
    min_val: float
    max_val: float
    median: float
    percentiles: Dict[int, float]
    distribution_stats: Dict[str, Any]
    sample_size: int
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSnapshot':
        """Create from dictionary."""
        return cls(**data)


class DriftDetector(ABC):
    """Abstract base class for drift detection algorithms."""
    
    @abstractmethod
    def detect_drift(self, reference_data: np.ndarray, current_data: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect drift between reference and current data.
        
        Args:
            reference_data: Reference data distribution
            current_data: Current data distribution
            
        Returns:
            Tuple of (is_drift_detected, drift_score, metadata)
        """
        pass


class KolmogorovSmirnovDetector(DriftDetector):
    """Kolmogorov-Smirnov drift detector."""
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize KS detector.
        
        Args:
            significance_level: Significance level for the test
        """
        self.significance_level = significance_level
    
    def detect_drift(self, reference_data: np.ndarray, current_data: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        """Detect drift using Kolmogorov-Smirnov test."""
        try:
            from scipy.stats import ks_2samp
            
            # Perform KS test
            statistic, p_value = ks_2samp(reference_data, current_data)
            
            # Determine if drift is detected
            is_drift = p_value < self.significance_level
            
            metadata = {
                "test_statistic": statistic,
                "p_value": p_value,
                "significance_level": self.significance_level,
                "test_name": "Kolmogorov-Smirnov"
            }
            
            return is_drift, statistic, metadata
            
        except ImportError:
            warnings.warn("scipy not available, using simplified drift detection")
            return self._simplified_drift_detection(reference_data, current_data)
    
    def _simplified_drift_detection(self, reference_data: np.ndarray, current_data: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        """Simplified drift detection without scipy."""
        # Compare means and standard deviations
        ref_mean, ref_std = np.mean(reference_data), np.std(reference_data)
        cur_mean, cur_std = np.mean(current_data), np.std(current_data)
        
        # Calculate normalized difference
        mean_diff = abs(cur_mean - ref_mean) / (ref_std + 1e-8)
        std_diff = abs(cur_std - ref_std) / (ref_std + 1e-8)
        
        # Combine differences
        drift_score = max(mean_diff, std_diff)
        
        # Simple threshold-based detection
        is_drift = drift_score > 2.0  # Roughly 2 standard deviations
        
        metadata = {
            "mean_difference": mean_diff,
            "std_difference": std_diff,
            "test_name": "Simplified Statistical"
        }
        
        return is_drift, drift_score, metadata


class PageHinkleyDetector(DriftDetector):
    """Page-Hinkley drift detector for sequential data."""
    
    def __init__(self, threshold: float = 50.0, alpha: float = 0.9999):
        """
        Initialize Page-Hinkley detector.
        
        Args:
            threshold: Detection threshold
            alpha: Forgetting factor
        """
        self.threshold = threshold
        self.alpha = alpha
        self.sum_positive = 0.0
        self.sum_negative = 0.0
        self.min_positive = 0.0
        self.max_negative = 0.0
    
    def detect_drift(self, reference_data: np.ndarray, current_data: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        """Detect drift using Page-Hinkley test."""
        # Calculate mean of reference data
        reference_mean = np.mean(reference_data)
        
        # Process current data points
        drift_detected = False
        max_drift_score = 0.0
        
        for value in current_data:
            # Calculate deviation from reference
            deviation = value - reference_mean
            
            # Update cumulative sums
            self.sum_positive = self.alpha * self.sum_positive + deviation
            self.sum_negative = self.alpha * self.sum_negative - deviation
            
            # Update min/max
            self.min_positive = min(self.min_positive, self.sum_positive)
            self.max_negative = max(self.max_negative, self.sum_negative)
            
            # Calculate drift scores
            positive_drift = self.sum_positive - self.min_positive
            negative_drift = self.sum_negative - self.max_negative
            
            drift_score = max(positive_drift, negative_drift)
            max_drift_score = max(max_drift_score, drift_score)
            
            # Check for drift
            if drift_score > self.threshold:
                drift_detected = True
                break
        
        metadata = {
            "positive_drift": positive_drift,
            "negative_drift": negative_drift,
            "threshold": self.threshold,
            "test_name": "Page-Hinkley"
        }
        
        return drift_detected, max_drift_score, metadata


class DDMDetector(DriftDetector):
    """Drift Detection Method (DDM) detector."""
    
    def __init__(self, warning_level: float = 2.0, drift_level: float = 3.0):
        """
        Initialize DDM detector.
        
        Args:
            warning_level: Warning level threshold
            drift_level: Drift level threshold
        """
        self.warning_level = warning_level
        self.drift_level = drift_level
        self.error_count = 0
        self.total_count = 0
        self.min_error_rate = float('inf')
        self.min_std = float('inf')
    
    def detect_drift(self, reference_data: np.ndarray, current_data: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        """Detect drift using DDM method."""
        # Assume current_data represents error indicators (0 or 1)
        if len(current_data) == 0:
            return False, 0.0, {"test_name": "DDM"}
        
        # Update error statistics
        self.error_count += np.sum(current_data)
        self.total_count += len(current_data)
        
        if self.total_count < 30:  # Need minimum samples
            return False, 0.0, {"test_name": "DDM"}
        
        # Calculate error rate and standard deviation
        error_rate = self.error_count / self.total_count
        std = np.sqrt(error_rate * (1 - error_rate) / self.total_count)
        
        # Update minimum values
        if error_rate + std < self.min_error_rate + self.min_std:
            self.min_error_rate = error_rate
            self.min_std = std
        
        # Calculate drift score
        drift_score = (error_rate + std - self.min_error_rate - self.min_std) / (self.min_std + 1e-8)
        
        # Check for drift
        is_drift = drift_score > self.drift_level
        
        metadata = {
            "error_rate": error_rate,
            "std": std,
            "drift_score": drift_score,
            "warning_level": self.warning_level,
            "drift_level": self.drift_level,
            "test_name": "DDM"
        }
        
        return is_drift, drift_score, metadata


class ConceptDriftDetector:
    """
    Comprehensive concept drift detection system.
    
    Features:
    - Multiple drift detection algorithms
    - Real-time monitoring
    - Statistical analysis
    - Alert system
    - Performance tracking
    - Adaptive thresholds
    - Historical analysis
    """
    
    def __init__(self,
                 reference_window_size: int = 1000,
                 detection_window_size: int = 200,
                 min_samples_for_detection: int = 100,
                 alert_threshold: float = 0.05,
                 severity_thresholds: Optional[Dict[str, float]] = None,
                 max_alerts: int = 10000,
                 max_snapshots: int = 1000):
        """
        Initialize the concept drift detector.
        
        Args:
            reference_window_size: Size of reference window
            detection_window_size: Size of detection window
            min_samples_for_detection: Minimum samples needed for detection
            alert_threshold: Threshold for generating alerts
            severity_thresholds: Thresholds for different severity levels
            max_alerts: Maximum number of alerts to store
            max_snapshots: Maximum number of snapshots to store
        """
        self.reference_window_size = reference_window_size
        self.detection_window_size = detection_window_size
        self.min_samples_for_detection = min_samples_for_detection
        self.alert_threshold = alert_threshold
        self.max_alerts = max_alerts
        self.max_snapshots = max_snapshots
        
        # Severity thresholds
        self.severity_thresholds = severity_thresholds or {
            "low": 0.05,
            "medium": 0.1,
            "high": 0.2,
            "critical": 0.5
        }
        
        # Data storage
        self._reference_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=reference_window_size))
        self._current_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=detection_window_size))
        self._alerts: deque = deque(maxlen=max_alerts)
        self._snapshots: deque = deque(maxlen=max_snapshots)
        
        # Drift detectors
        self._detectors: Dict[str, DriftDetector] = {
            "ks": KolmogorovSmirnovDetector(),
            "page_hinkley": PageHinkleyDetector(),
            "ddm": DDMDetector()
        }
        
        # Statistics
        self._stats = {
            "total_samples": 0,
            "total_alerts": 0,
            "features_monitored": 0,
            "drift_detection_rate": 0.0,
            "last_drift_timestamp": None,
            "alerts_by_severity": {severity.value: 0 for severity in DriftSeverity},
            "alerts_by_type": {drift_type.value: 0 for drift_type in DriftType}
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Event callbacks
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Feature monitoring
        self._feature_enabled: Dict[str, bool] = {}
        self._feature_last_update: Dict[str, float] = {}
    
    def add_sample(self, feature_name: str, value: Union[float, np.ndarray], is_reference: bool = False) -> None:
        """
        Add a sample for drift detection.
        
        Args:
            feature_name: Name of the feature
            value: Feature value(s)
            is_reference: Whether this is reference data
        """
        with self._lock:
            # Convert to numpy array if needed
            if not isinstance(value, np.ndarray):
                value = np.array([value])
            
            # Enable feature monitoring if not already enabled
            if feature_name not in self._feature_enabled:
                self._feature_enabled[feature_name] = True
                self._stats["features_monitored"] += 1
            
            # Add to appropriate data store
            if is_reference:
                self._reference_data[feature_name].extend(value)
            else:
                self._current_data[feature_name].extend(value)
            
            # Update statistics
            self._stats["total_samples"] += len(value)
            self._feature_last_update[feature_name] = time.time()
            
            # Create snapshot if enough data
            if len(self._current_data[feature_name]) >= self.min_samples_for_detection:
                self._create_snapshot(feature_name)
            
            # Check for drift
            self._check_drift(feature_name)
    
    def _create_snapshot(self, feature_name: str) -> None:
        """Create a data snapshot for a feature."""
        current_data = np.array(self._current_data[feature_name])
        
        if len(current_data) == 0:
            return
        
        # Calculate statistics
        percentiles = {p: np.percentile(current_data, p) for p in [25, 50, 75, 90, 95, 99]}
        
        snapshot = DataSnapshot(
            timestamp=time.time(),
            feature_name=feature_name,
            mean=np.mean(current_data),
            std=np.std(current_data),
            min_val=np.min(current_data),
            max_val=np.max(current_data),
            median=np.median(current_data),
            percentiles=percentiles,
            distribution_stats={
                "skewness": self._calculate_skewness(current_data),
                "kurtosis": self._calculate_kurtosis(current_data)
            },
            sample_size=len(current_data)
        )
        
        self._snapshots.append(snapshot)
    
    def _check_drift(self, feature_name: str) -> None:
        """Check for drift in a specific feature."""
        # Need enough data in both reference and current windows
        if (len(self._reference_data[feature_name]) < self.min_samples_for_detection or
            len(self._current_data[feature_name]) < self.min_samples_for_detection):
            return
        
        reference_data = np.array(self._reference_data[feature_name])
        current_data = np.array(self._current_data[feature_name])
        
        # Run drift detection algorithms
        for detector_name, detector in self._detectors.items():
            try:
                is_drift, drift_score, metadata = detector.detect_drift(reference_data, current_data)
                
                if is_drift and drift_score > self.alert_threshold:
                    self._generate_alert(feature_name, drift_score, detector_name, metadata)
                    
            except Exception as e:
                # Log error but continue with other detectors
                continue
    
    def _generate_alert(self, feature_name: str, drift_score: float, detector_name: str, metadata: Dict[str, Any]) -> None:
        """Generate a drift alert."""
        # Determine severity
        severity = self._determine_severity(drift_score)
        
        # Determine drift type (simplified classification)
        drift_type = self._classify_drift_type(feature_name, drift_score)
        
        # Create alert
        alert = DriftAlert(
            timestamp=time.time(),
            drift_type=drift_type,
            severity=severity,
            feature_name=feature_name,
            drift_score=drift_score,
            threshold=self.alert_threshold,
            description=f"Drift detected in {feature_name} using {detector_name}",
            statistical_test=detector_name,
            p_value=metadata.get("p_value"),
            effect_size=drift_score,
            metadata=metadata
        )
        
        # Store alert
        self._alerts.append(alert)
        
        # Update statistics
        self._stats["total_alerts"] += 1
        self._stats["alerts_by_severity"][severity.value] += 1
        self._stats["alerts_by_type"][drift_type.value] += 1
        self._stats["last_drift_timestamp"] = alert.timestamp
        
        # Update drift detection rate
        total_checks = self._stats["total_samples"] / self.min_samples_for_detection
        self._stats["drift_detection_rate"] = self._stats["total_alerts"] / max(1, total_checks)
        
        # Trigger callbacks
        self._trigger_callbacks("drift_detected", alert)
    
    def _determine_severity(self, drift_score: float) -> DriftSeverity:
        """Determine the severity of drift based on score."""
        if drift_score >= self.severity_thresholds["critical"]:
            return DriftSeverity.CRITICAL
        elif drift_score >= self.severity_thresholds["high"]:
            return DriftSeverity.HIGH
        elif drift_score >= self.severity_thresholds["medium"]:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    def _classify_drift_type(self, feature_name: str, drift_score: float) -> DriftType:
        """Classify the type of drift (simplified)."""
        # This is a simplified classification - in practice, you'd use more sophisticated methods
        recent_alerts = [a for a in self._alerts if a.feature_name == feature_name and 
                        time.time() - a.timestamp < 3600]  # Last hour
        
        if len(recent_alerts) > 3:
            return DriftType.GRADUAL
        elif drift_score > 0.3:
            return DriftType.SUDDEN
        else:
            return DriftType.INCREMENTAL
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data."""
        if len(data) < 3:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return 0.0
        
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data."""
        if len(data) < 4:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return 0.0
        
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def get_alerts(self, 
                   feature_name: Optional[str] = None,
                   severity: Optional[DriftSeverity] = None,
                   time_range: Optional[Tuple[float, float]] = None,
                   limit: Optional[int] = None) -> List[DriftAlert]:
        """
        Get drift alerts with optional filtering.
        
        Args:
            feature_name: Filter by feature name
            severity: Filter by severity
            time_range: Filter by time range (start, end)
            limit: Maximum number of alerts to return
            
        Returns:
            List of drift alerts
        """
        with self._lock:
            alerts = list(self._alerts)
            
            # Apply filters
            if feature_name:
                alerts = [a for a in alerts if a.feature_name == feature_name]
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            if time_range:
                start_time, end_time = time_range
                alerts = [a for a in alerts if start_time <= a.timestamp <= end_time]
            
            # Sort by timestamp (most recent first)
            alerts.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                alerts = alerts[:limit]
            
            return alerts
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get drift detection statistics."""
        with self._lock:
            return self._stats.copy()
    
    def get_feature_summary(self, feature_name: str) -> Dict[str, Any]:
        """Get summary statistics for a specific feature."""
        with self._lock:
            if feature_name not in self._reference_data:
                return {}
            
            reference_data = np.array(self._reference_data[feature_name])
            current_data = np.array(self._current_data[feature_name])
            
            return {
                "feature_name": feature_name,
                "reference_samples": len(reference_data),
                "current_samples": len(current_data),
                "reference_mean": np.mean(reference_data) if len(reference_data) > 0 else 0,
                "current_mean": np.mean(current_data) if len(current_data) > 0 else 0,
                "reference_std": np.std(reference_data) if len(reference_data) > 0 else 0,
                "current_std": np.std(current_data) if len(current_data) > 0 else 0,
                "last_update": self._feature_last_update.get(feature_name, 0),
                "enabled": self._feature_enabled.get(feature_name, False)
            }
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """
        Add a callback for drift events.
        
        Args:
            event: Event name ("drift_detected", "alert_generated")
            callback: Callback function
        """
        with self._lock:
            self._callbacks[event].append(callback)
    
    def remove_callback(self, event: str, callback: Callable) -> None:
        """
        Remove a callback for drift events.
        
        Args:
            event: Event name
            callback: Callback function
        """
        with self._lock:
            if callback in self._callbacks[event]:
                self._callbacks[event].remove(callback)
    
    def _trigger_callbacks(self, event: str, data: Any) -> None:
        """Trigger callbacks for an event."""
        for callback in self._callbacks[event]:
            try:
                callback(data)
            except Exception as e:
                # Log error but continue
                continue
    
    def reset_feature(self, feature_name: str) -> None:
        """Reset data for a specific feature."""
        with self._lock:
            if feature_name in self._reference_data:
                del self._reference_data[feature_name]
            if feature_name in self._current_data:
                del self._current_data[feature_name]
            if feature_name in self._feature_enabled:
                del self._feature_enabled[feature_name]
            if feature_name in self._feature_last_update:
                del self._feature_last_update[feature_name]
    
    def clear_alerts(self) -> None:
        """Clear all drift alerts."""
        with self._lock:
            self._alerts.clear()
    
    def export_data(self, feature_name: str) -> Dict[str, Any]:
        """Export data for a specific feature."""
        with self._lock:
            return {
                "feature_name": feature_name,
                "reference_data": list(self._reference_data.get(feature_name, [])),
                "current_data": list(self._current_data.get(feature_name, [])),
                "alerts": [alert.to_dict() for alert in self._alerts if alert.feature_name == feature_name],
                "snapshots": [snapshot.to_dict() for snapshot in self._snapshots if snapshot.feature_name == feature_name]
            }
    
    def __len__(self) -> int:
        """Get total number of alerts."""
        with self._lock:
            return len(self._alerts) 