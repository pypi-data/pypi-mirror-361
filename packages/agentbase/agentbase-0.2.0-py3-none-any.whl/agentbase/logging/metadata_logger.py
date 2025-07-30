"""
Metadata Logger - Store hyperparameters, performance metrics, and training metadata.

This module provides comprehensive logging capabilities for tracking training
progress, system performance, and experimental configurations.
"""

import json
import threading
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import os
import pickle
import gzip
from pathlib import Path
import csv


class LogLevel(Enum):
    """Log levels for different types of metadata."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics that can be logged."""
    SCALAR = "scalar"
    VECTOR = "vector"
    HISTOGRAM = "histogram"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    CUSTOM = "custom"


@dataclass
class LogEntry:
    """
    A single log entry with metadata.
    """
    timestamp: float
    level: LogLevel
    category: str
    message: str
    data: Dict[str, Any]
    tags: List[str]
    source: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["level"] = self.level.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create from dictionary."""
        data["level"] = LogLevel(data["level"])
        return cls(**data)


@dataclass
class MetricEntry:
    """
    A single metric entry.
    """
    timestamp: float
    name: str
    value: Any
    metric_type: MetricType
    step: int
    epoch: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["metric_type"] = self.metric_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricEntry':
        """Create from dictionary."""
        data["metric_type"] = MetricType(data["metric_type"])
        return cls(**data)


@dataclass
class ExperimentConfig:
    """
    Configuration for an experiment.
    """
    experiment_id: str
    name: str
    description: str
    hyperparameters: Dict[str, Any]
    model_config: Dict[str, Any]
    data_config: Dict[str, Any]
    training_config: Dict[str, Any]
    created_at: float
    tags: List[str]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentConfig':
        """Create from dictionary."""
        return cls(**data)


class MetadataLogger:
    """
    Comprehensive metadata logging system for AI agent training and operations.
    
    Features:
    - Structured logging with multiple levels
    - Metric tracking with various types
    - Experiment configuration management
    - Performance monitoring
    - Export to multiple formats (JSON, CSV, TensorBoard)
    - Real-time statistics
    - Thread-safe operations
    - Automatic cleanup and archiving
    """
    
    def __init__(self,
                 log_dir: str = "./logs",
                 max_log_entries: int = 100000,
                 max_metrics: int = 500000,
                 auto_save_interval: int = 1000,
                 enable_file_logging: bool = True,
                 enable_console_logging: bool = True,
                 log_level: LogLevel = LogLevel.INFO,
                 compress_old_logs: bool = True,
                 max_log_files: int = 10):
        """
        Initialize the metadata logger.
        
        Args:
            log_dir: Directory to store log files
            max_log_entries: Maximum number of log entries to keep in memory
            max_metrics: Maximum number of metrics to keep in memory
            auto_save_interval: Auto-save every N entries
            enable_file_logging: Whether to write logs to files
            enable_console_logging: Whether to print logs to console
            log_level: Minimum log level to record
            compress_old_logs: Whether to compress old log files
            max_log_files: Maximum number of log files to keep
        """
        self.log_dir = Path(log_dir)
        self.max_log_entries = max_log_entries
        self.max_metrics = max_metrics
        self.auto_save_interval = auto_save_interval
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        self.log_level = log_level
        self.compress_old_logs = compress_old_logs
        self.max_log_files = max_log_files
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage
        self._log_entries: deque = deque(maxlen=max_log_entries)
        self._metrics: deque = deque(maxlen=max_metrics)
        self._experiments: Dict[str, ExperimentConfig] = {}
        
        # Indexes for fast lookup
        self._logs_by_category: Dict[str, List[LogEntry]] = defaultdict(list)
        self._metrics_by_name: Dict[str, List[MetricEntry]] = defaultdict(list)
        self._logs_by_tag: Dict[str, List[LogEntry]] = defaultdict(list)
        
        # Current experiment
        self._current_experiment: Optional[ExperimentConfig] = None
        self._current_step = 0
        self._current_epoch = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            "total_logs": 0,
            "total_metrics": 0,
            "total_experiments": 0,
            "logs_by_level": {level.value: 0 for level in LogLevel},
            "metrics_by_type": {metric_type.value: 0 for metric_type in MetricType},
            "uptime": time.time(),
        }
        
        # File handles
        self._log_file_handle = None
        self._metrics_file_handle = None
        
        # Auto-save counter
        self._save_counter = 0
        
        # Event hooks
        self._hooks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Initialize file logging
        if self.enable_file_logging:
            self._init_file_logging()
    
    def _init_file_logging(self) -> None:
        """Initialize file logging."""
        # Create log files
        log_file = self.log_dir / f"agentbase_{int(time.time())}.log"
        metrics_file = self.log_dir / f"metrics_{int(time.time())}.csv"
        
        # Open file handles
        self._log_file_handle = open(log_file, 'w', encoding='utf-8')
        self._metrics_file_handle = open(metrics_file, 'w', newline='', encoding='utf-8')
        
        # Initialize CSV writer for metrics
        self._metrics_csv_writer = csv.writer(self._metrics_file_handle)
        self._metrics_csv_writer.writerow([
            "timestamp", "name", "value", "metric_type", "step", "epoch", "tags", "metadata"
        ])
    
    def log(self,
            level: LogLevel,
            category: str,
            message: str,
            data: Optional[Dict[str, Any]] = None,
            tags: Optional[List[str]] = None,
            source: str = "agentbase",
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a message with metadata.
        
        Args:
            level: Log level
            category: Category of the log
            message: Log message
            data: Additional data to log
            tags: Tags for categorization
            source: Source of the log
            metadata: Additional metadata
        """
        # Check if we should log this level
        if level.value < self.log_level.value and level != LogLevel.CRITICAL:
            return
        
        with self._lock:
            # Create log entry
            entry = LogEntry(
                timestamp=time.time(),
                level=level,
                category=category,
                message=message,
                data=data or {},
                tags=tags or [],
                source=source,
                metadata=metadata
            )
            
            # Store in memory
            self._log_entries.append(entry)
            
            # Update indexes
            self._logs_by_category[category].append(entry)
            for tag in entry.tags:
                self._logs_by_tag[tag].append(entry)
            
            # Update statistics
            self._stats["total_logs"] += 1
            self._stats["logs_by_level"][level.value] += 1
            
            # Console logging
            if self.enable_console_logging:
                self._print_log_entry(entry)
            
            # File logging
            if self.enable_file_logging and self._log_file_handle:
                self._write_log_entry(entry)
            
            # Trigger hooks
            self._trigger_hooks("log", entry)
            
            # Auto-save
            self._maybe_auto_save()
    
    def log_metric(self,
                   name: str,
                   value: Any,
                   metric_type: MetricType = MetricType.SCALAR,
                   step: Optional[int] = None,
                   epoch: Optional[int] = None,
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a metric value.
        
        Args:
            name: Name of the metric
            value: Value of the metric
            metric_type: Type of metric
            step: Training step
            epoch: Training epoch
            tags: Tags for categorization
            metadata: Additional metadata
        """
        with self._lock:
            # Use current step/epoch if not provided
            current_step = step if step is not None else self._current_step
            current_epoch = epoch if epoch is not None else self._current_epoch
            
            # Create metric entry
            entry = MetricEntry(
                timestamp=time.time(),
                name=name,
                value=value,
                metric_type=metric_type,
                step=current_step,
                epoch=current_epoch,
                tags=tags,
                metadata=metadata
            )
            
            # Store in memory
            self._metrics.append(entry)
            
            # Update indexes
            self._metrics_by_name[name].append(entry)
            
            # Update statistics
            self._stats["total_metrics"] += 1
            self._stats["metrics_by_type"][metric_type.value] += 1
            
            # File logging
            if self.enable_file_logging and self._metrics_csv_writer:
                self._write_metric_entry(entry)
            
            # Trigger hooks
            self._trigger_hooks("metric", entry)
            
            # Auto-save
            self._maybe_auto_save()
    
    def start_experiment(self,
                        name: str,
                        description: str,
                        hyperparameters: Dict[str, Any],
                        model_config: Dict[str, Any],
                        data_config: Dict[str, Any],
                        training_config: Dict[str, Any],
                        tags: Optional[List[str]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new experiment.
        
        Args:
            name: Name of the experiment
            description: Description of the experiment
            hyperparameters: Hyperparameters used
            model_config: Model configuration
            data_config: Data configuration
            training_config: Training configuration
            tags: Tags for categorization
            metadata: Additional metadata
            
        Returns:
            Experiment ID
        """
        with self._lock:
            # Generate experiment ID
            experiment_id = f"exp_{int(time.time() * 1000)}"
            
            # Create experiment config
            config = ExperimentConfig(
                experiment_id=experiment_id,
                name=name,
                description=description,
                hyperparameters=hyperparameters,
                model_config=model_config,
                data_config=data_config,
                training_config=training_config,
                created_at=time.time(),
                tags=tags or [],
                metadata=metadata
            )
            
            # Store experiment
            self._experiments[experiment_id] = config
            self._current_experiment = config
            
            # Reset counters
            self._current_step = 0
            self._current_epoch = 0
            
            # Update statistics
            self._stats["total_experiments"] += 1
            
            # Log experiment start
            self.log(LogLevel.INFO, "experiment", f"Started experiment: {name}",
                    {"experiment_id": experiment_id, "config": config.to_dict()})
            
            # Trigger hooks
            self._trigger_hooks("experiment_start", config)
            
            return experiment_id
    
    def end_experiment(self, results: Optional[Dict[str, Any]] = None) -> None:
        """
        End the current experiment.
        
        Args:
            results: Final results of the experiment
        """
        with self._lock:
            if not self._current_experiment:
                return
            
            # Log experiment end
            self.log(LogLevel.INFO, "experiment", 
                    f"Ended experiment: {self._current_experiment.name}",
                    {"experiment_id": self._current_experiment.experiment_id, 
                     "results": results or {}})
            
            # Trigger hooks
            self._trigger_hooks("experiment_end", self._current_experiment)
            
            # Clear current experiment
            self._current_experiment = None
    
    def step(self) -> None:
        """Increment the current step counter."""
        with self._lock:
            self._current_step += 1
    
    def epoch(self) -> None:
        """Increment the current epoch counter."""
        with self._lock:
            self._current_epoch += 1
    
    def get_logs(self,
                 category: Optional[str] = None,
                 level: Optional[LogLevel] = None,
                 tags: Optional[List[str]] = None,
                 limit: Optional[int] = None) -> List[LogEntry]:
        """
        Get log entries with optional filtering.
        
        Args:
            category: Filter by category
            level: Filter by log level
            tags: Filter by tags
            limit: Maximum number of entries to return
            
        Returns:
            List of log entries
        """
        with self._lock:
            logs = list(self._log_entries)
            
            # Apply filters
            if category:
                logs = [log for log in logs if log.category == category]
            if level:
                logs = [log for log in logs if log.level == level]
            if tags:
                logs = [log for log in logs if any(tag in log.tags for tag in tags)]
            
            # Apply limit
            if limit:
                logs = logs[-limit:]
            
            return logs
    
    def get_metrics(self,
                    name: Optional[str] = None,
                    metric_type: Optional[MetricType] = None,
                    step_range: Optional[Tuple[int, int]] = None,
                    limit: Optional[int] = None) -> List[MetricEntry]:
        """
        Get metric entries with optional filtering.
        
        Args:
            name: Filter by metric name
            metric_type: Filter by metric type
            step_range: Filter by step range (min, max)
            limit: Maximum number of entries to return
            
        Returns:
            List of metric entries
        """
        with self._lock:
            metrics = list(self._metrics)
            
            # Apply filters
            if name:
                metrics = [m for m in metrics if m.name == name]
            if metric_type:
                metrics = [m for m in metrics if m.metric_type == metric_type]
            if step_range:
                min_step, max_step = step_range
                metrics = [m for m in metrics if min_step <= m.step <= max_step]
            
            # Apply limit
            if limit:
                metrics = metrics[-limit:]
            
            return metrics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logger statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats["uptime"] = time.time() - stats["uptime"]
            stats["current_step"] = self._current_step
            stats["current_epoch"] = self._current_epoch
            stats["current_experiment"] = (
                self._current_experiment.experiment_id if self._current_experiment else None
            )
            return stats
    
    def export_logs(self, path: str, format: str = "json") -> None:
        """
        Export logs to a file.
        
        Args:
            path: Path to export to
            format: Export format ("json", "csv")
        """
        with self._lock:
            if format == "json":
                data = {
                    "logs": [entry.to_dict() for entry in self._log_entries],
                    "metrics": [entry.to_dict() for entry in self._metrics],
                    "experiments": {k: v.to_dict() for k, v in self._experiments.items()},
                    "stats": self._stats
                }
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format == "csv":
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "timestamp", "level", "category", "message", "data", "tags", "source"
                    ])
                    for entry in self._log_entries:
                        writer.writerow([
                            entry.timestamp, entry.level.value, entry.category,
                            entry.message, json.dumps(entry.data), 
                            json.dumps(entry.tags), entry.source
                        ])
    
    def add_hook(self, event: str, callback: Callable) -> None:
        """
        Add a hook for specific events.
        
        Args:
            event: Event name ("log", "metric", "experiment_start", "experiment_end")
            callback: Callback function
        """
        with self._lock:
            self._hooks[event].append(callback)
    
    def remove_hook(self, event: str, callback: Callable) -> None:
        """
        Remove a hook for specific events.
        
        Args:
            event: Event name
            callback: Callback function
        """
        with self._lock:
            if callback in self._hooks[event]:
                self._hooks[event].remove(callback)
    
    def _print_log_entry(self, entry: LogEntry) -> None:
        """Print log entry to console."""
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.timestamp))
        print(f"[{timestamp_str}] {entry.level.value.upper()} - {entry.category}: {entry.message}")
        if entry.data:
            print(f"  Data: {entry.data}")
    
    def _write_log_entry(self, entry: LogEntry) -> None:
        """Write log entry to file."""
        if self._log_file_handle:
            self._log_file_handle.write(json.dumps(entry.to_dict()) + "\n")
            self._log_file_handle.flush()
    
    def _write_metric_entry(self, entry: MetricEntry) -> None:
        """Write metric entry to CSV file."""
        if self._metrics_csv_writer:
            self._metrics_csv_writer.writerow([
                entry.timestamp, entry.name, entry.value, entry.metric_type.value,
                entry.step, entry.epoch, json.dumps(entry.tags), 
                json.dumps(entry.metadata)
            ])
            self._metrics_file_handle.flush()
    
    def _trigger_hooks(self, event: str, data: Any) -> None:
        """Trigger hooks for an event."""
        for hook in self._hooks[event]:
            try:
                hook(data)
            except Exception as e:
                print(f"Hook error for event '{event}': {e}")
    
    def _maybe_auto_save(self) -> None:
        """Auto-save if counter reached."""
        self._save_counter += 1
        if self._save_counter >= self.auto_save_interval:
            self._save_counter = 0
            self._cleanup_old_files()
    
    def _cleanup_old_files(self) -> None:
        """Cleanup old log files."""
        if not self.enable_file_logging:
            return
        
        # Get all log files
        log_files = list(self.log_dir.glob("agentbase_*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime)
        
        # Remove old files
        while len(log_files) > self.max_log_files:
            old_file = log_files.pop(0)
            if self.compress_old_logs:
                # Compress before deletion
                with open(old_file, 'rb') as f_in:
                    with gzip.open(f"{old_file}.gz", 'wb') as f_out:
                        f_out.writelines(f_in)
            old_file.unlink()
    
    def close(self) -> None:
        """Close the logger and cleanup resources."""
        with self._lock:
            if self._log_file_handle:
                self._log_file_handle.close()
                self._log_file_handle = None
            
            if self._metrics_file_handle:
                self._metrics_file_handle.close()
                self._metrics_file_handle = None
    
    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 