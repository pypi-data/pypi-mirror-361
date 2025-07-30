"""
AgentBase - Main class that integrates all learning and adaptation components.

This module provides the central AgentBase class that orchestrates memory management,
experience replay, lifelong learning, metadata logging, and concept drift detection.
"""

import time
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import logging

from ..memory.cache import MemoryCache
from ..memory.replay_buffer import ExperienceReplayBuffer
from ..memory.lifelong_learning import LifelongLearningStore, UpdateType, MistakeType
from ..logging.metadata_logger import MetadataLogger, LogLevel, MetricType
from ..drift.concept_drift import ConceptDriftDetector, DriftSeverity


@dataclass
class AgentConfig:
    """Configuration for the AgentBase instance."""
    agent_id: str
    name: str
    description: str
    version: str = "1.0.0"
    
    # Memory configuration
    cache_size: int = 10000
    cache_ttl: Optional[float] = None
    cache_eviction_policy: str = "lru"
    
    # Replay buffer configuration
    replay_buffer_capacity: int = 100000
    replay_sampling_strategy: str = "uniform"
    min_replay_size: int = 1000
    
    # Lifelong learning configuration
    max_model_updates: int = 10000
    max_mistakes: int = 50000
    max_corrections: int = 25000
    
    # Logging configuration
    log_level: str = "INFO"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    log_dir: str = "./logs"
    
    # Drift detection configuration
    drift_detection_enabled: bool = True
    drift_reference_window: int = 1000
    drift_detection_window: int = 200
    drift_alert_threshold: float = 0.05
    
    # Storage configuration
    storage_dir: str = "./storage"
    auto_save_interval: int = 1000
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    performance_metrics_interval: float = 60.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create from dictionary."""
        return cls(**data)


class AgentBase:
    """
    Main AgentBase class that integrates all learning and adaptation components.
    
    Features:
    - Memory management with fast caching
    - Experience replay for reinforcement learning
    - Lifelong learning with mistake tracking
    - Comprehensive metadata logging
    - Concept drift detection
    - Performance monitoring
    - Thread-safe operations
    - Persistent storage
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, config_path: Optional[str] = None):
        """
        Initialize AgentBase.
        
        Args:
            config: Agent configuration
            config_path: Path to configuration file
        """
        # Load configuration
        if config_path:
            self.config = self._load_config(config_path)
        elif config:
            self.config = config
        else:
            self.config = AgentConfig(
                agent_id=f"agent_{int(time.time())}",
                name="Default Agent",
                description="AgentBase instance with default configuration"
            )
        
        # Initialize logging first
        self._setup_logging()
        
        # Initialize components
        self._setup_components()
        
        # Performance monitoring
        self._setup_performance_monitoring()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # State tracking
        self._is_running = False
        self._start_time = time.time()
        self._operation_count = 0
        
        # Event hooks
        self._hooks: Dict[str, List[Callable]] = {}
        
        # Statistics
        self._stats = {
            "uptime": 0.0,
            "operations_performed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "experiences_stored": 0,
            "mistakes_recorded": 0,
            "corrections_applied": 0,
            "drift_alerts": 0,
            "performance_score": 0.0,
        }
        
        # Log initialization
        self.logger.log(LogLevel.INFO, "initialization", "AgentBase initialized successfully", {
            "agent_id": self.config.agent_id,
            "config": self.config.to_dict()
        })
        
        # Start background processes
        self._start_background_processes()
    
    def _load_config(self, config_path: str) -> AgentConfig:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return AgentConfig.from_dict(config_data)
        except Exception as e:
            # Fall back to default config
            return AgentConfig(
                agent_id=f"agent_{int(time.time())}",
                name="Default Agent",
                description="AgentBase instance with default configuration"
            )
    
    def _setup_logging(self) -> None:
        """Setup the metadata logger."""
        log_level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "CRITICAL": LogLevel.CRITICAL
        }
        
        self.logger = MetadataLogger(
            log_dir=self.config.log_dir,
            enable_file_logging=self.config.enable_file_logging,
            enable_console_logging=self.config.enable_console_logging,
            log_level=log_level_map.get(self.config.log_level, LogLevel.INFO)
        )
    
    def _setup_components(self) -> None:
        """Setup all components."""
        # Memory cache
        self.cache = MemoryCache(
            max_size=self.config.cache_size,
            default_ttl=self.config.cache_ttl,
            eviction_policy=self.config.cache_eviction_policy
        )
        
        # Experience replay buffer
        self.replay_buffer = ExperienceReplayBuffer(
            capacity=self.config.replay_buffer_capacity,
            sampling_strategy=self.config.replay_sampling_strategy,
            min_size_to_sample=self.config.min_replay_size
        )
        
        # Lifelong learning store
        storage_path = Path(self.config.storage_dir) / f"{self.config.agent_id}_lifelong_learning.gz"
        self.lifelong_learning = LifelongLearningStore(
            max_updates=self.config.max_model_updates,
            max_mistakes=self.config.max_mistakes,
            max_corrections=self.config.max_corrections,
            save_path=str(storage_path),
            auto_save_interval=self.config.auto_save_interval
        )
        
        # Concept drift detector
        if self.config.drift_detection_enabled:
            self.drift_detector = ConceptDriftDetector(
                reference_window_size=self.config.drift_reference_window,
                detection_window_size=self.config.drift_detection_window,
                alert_threshold=self.config.drift_alert_threshold
            )
            
            # Add drift detection callback
            self.drift_detector.add_callback("drift_detected", self._on_drift_detected)
        else:
            self.drift_detector = None
    
    def _setup_performance_monitoring(self) -> None:
        """Setup performance monitoring."""
        if self.config.enable_performance_monitoring:
            # Start performance monitoring thread
            self._performance_thread = threading.Thread(target=self._performance_monitor, daemon=True)
            self._performance_thread.start()
    
    def _start_background_processes(self) -> None:
        """Start background processes."""
        self._is_running = True
        
        # Start statistics collection thread
        self._stats_thread = threading.Thread(target=self._stats_collector, daemon=True)
        self._stats_thread.start()
    
    def _performance_monitor(self) -> None:
        """Monitor performance metrics."""
        while self._is_running:
            try:
                # Collect performance metrics
                cache_stats = self.cache.get_stats()
                replay_stats = self.replay_buffer.get_stats()
                learning_stats = self.lifelong_learning.get_statistics()
                
                # Log performance metrics
                self.logger.log_metric("cache_hit_rate", cache_stats["hit_rate"], MetricType.SCALAR)
                self.logger.log_metric("cache_size", cache_stats["current_size"], MetricType.SCALAR)
                self.logger.log_metric("replay_buffer_size", replay_stats["current_size"], MetricType.SCALAR)
                self.logger.log_metric("total_experiences", replay_stats["total_added"], MetricType.SCALAR)
                self.logger.log_metric("learning_velocity", learning_stats["learning_velocity"], MetricType.SCALAR)
                
                if self.drift_detector:
                    drift_stats = self.drift_detector.get_statistics()
                    self.logger.log_metric("drift_detection_rate", drift_stats["drift_detection_rate"], MetricType.SCALAR)
                    self.logger.log_metric("drift_alerts", drift_stats["total_alerts"], MetricType.SCALAR)
                
                # Sleep until next monitoring cycle
                time.sleep(self.config.performance_metrics_interval)
                
            except Exception as e:
                self.logger.log(LogLevel.ERROR, "performance_monitoring", f"Error in performance monitoring: {e}")
                time.sleep(self.config.performance_metrics_interval)
    
    def _stats_collector(self) -> None:
        """Collect and update statistics."""
        while self._is_running:
            try:
                with self._lock:
                    # Update basic stats
                    self._stats["uptime"] = time.time() - self._start_time
                    self._stats["operations_performed"] = self._operation_count
                    
                    # Update component stats
                    cache_stats = self.cache.get_stats()
                    self._stats["cache_hits"] = cache_stats["hits"]
                    self._stats["cache_misses"] = cache_stats["misses"]
                    
                    replay_stats = self.replay_buffer.get_stats()
                    self._stats["experiences_stored"] = replay_stats["total_added"]
                    
                    learning_stats = self.lifelong_learning.get_statistics()
                    self._stats["mistakes_recorded"] = learning_stats["total_mistakes"]
                    self._stats["corrections_applied"] = learning_stats["total_corrections"]
                    
                    if self.drift_detector:
                        drift_stats = self.drift_detector.get_statistics()
                        self._stats["drift_alerts"] = drift_stats["total_alerts"]
                    
                    # Calculate performance score
                    self._stats["performance_score"] = self._calculate_performance_score()
                
                # Sleep until next collection cycle
                time.sleep(10.0)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.log(LogLevel.ERROR, "stats_collection", f"Error in stats collection: {e}")
                time.sleep(10.0)
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score."""
        try:
            # Weighted combination of various metrics
            cache_performance = self.cache.get_stats()["hit_rate"] / 100.0
            
            # Learning effectiveness (corrections success rate)
            learning_stats = self.lifelong_learning.get_statistics()
            learning_effectiveness = learning_stats["correction_success_rate"]
            
            # Drift detection responsiveness (inverse of drift rate)
            drift_responsiveness = 1.0
            if self.drift_detector:
                drift_stats = self.drift_detector.get_statistics()
                drift_rate = drift_stats["drift_detection_rate"]
                drift_responsiveness = max(0.0, 1.0 - drift_rate)
            
            # Weighted average
            score = (0.4 * cache_performance + 
                    0.4 * learning_effectiveness + 
                    0.2 * drift_responsiveness)
            
            return min(1.0, max(0.0, score))
            
        except Exception:
            return 0.0
    
    def _on_drift_detected(self, alert) -> None:
        """Handle drift detection alerts."""
        self.logger.log(LogLevel.WARNING, "drift_detection", 
                       f"Concept drift detected: {alert.description}", {
                           "feature": alert.feature_name,
                           "severity": alert.severity.value,
                           "drift_score": alert.drift_score
                       })
        
        # Trigger hook if registered
        if "drift_detected" in self._hooks:
            for hook in self._hooks["drift_detected"]:
                try:
                    hook(alert)
                except Exception as e:
                    self.logger.log(LogLevel.ERROR, "hook_execution", f"Error in drift hook: {e}")
    
    def store_experience(self, 
                        state: Any, 
                        action: Any, 
                        reward: float, 
                        next_state: Any, 
                        done: bool,
                        **kwargs) -> None:
        """
        Store an experience in the replay buffer.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
            **kwargs: Additional parameters
        """
        with self._lock:
            self._operation_count += 1
            
            # Store in replay buffer
            self.replay_buffer.add(state, action, reward, next_state, done, **kwargs)
            
            # Monitor for drift if enabled
            if self.drift_detector and isinstance(reward, (int, float)):
                self.drift_detector.add_sample("reward", reward)
            
            # Log the experience
            self.logger.log(LogLevel.DEBUG, "experience", "Experience stored", {
                "reward": reward,
                "done": done,
                "metadata": kwargs
            })
    
    def sample_experiences(self, batch_size: int) -> Optional[List]:
        """
        Sample experiences from the replay buffer.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of sampled experiences or None if not ready
        """
        with self._lock:
            self._operation_count += 1
            
            experiences = self.replay_buffer.sample(batch_size)
            
            if experiences:
                self.logger.log(LogLevel.DEBUG, "sampling", f"Sampled {len(experiences)} experiences")
            
            return experiences
    
    def record_mistake(self, 
                      mistake_type: MistakeType,
                      context: Dict[str, Any],
                      expected_output: Any,
                      actual_output: Any,
                      error_magnitude: float,
                      **kwargs) -> str:
        """
        Record a mistake made by the agent.
        
        Args:
            mistake_type: Type of mistake
            context: Context where mistake occurred
            expected_output: Expected output
            actual_output: Actual output
            error_magnitude: Magnitude of error
            **kwargs: Additional parameters
            
        Returns:
            Mistake ID
        """
        with self._lock:
            self._operation_count += 1
            
            mistake_id = self.lifelong_learning.record_mistake(
                mistake_type, context, expected_output, actual_output,
                error_magnitude, **kwargs
            )
            
            # Monitor error magnitude for drift
            if self.drift_detector:
                self.drift_detector.add_sample("error_magnitude", error_magnitude)
            
            self.logger.log(LogLevel.WARNING, "mistake", f"Mistake recorded: {mistake_type.value}", {
                "mistake_id": mistake_id,
                "error_magnitude": error_magnitude,
                "context": context
            })
            
            return mistake_id
    
    def apply_correction(self, 
                        mistake_id: str,
                        correction_type: str,
                        correction_data: Dict[str, Any],
                        success_rate: float,
                        **kwargs) -> str:
        """
        Apply a correction to fix a mistake.
        
        Args:
            mistake_id: ID of the mistake to correct
            correction_type: Type of correction
            correction_data: Correction data
            success_rate: Success rate of the correction
            **kwargs: Additional parameters
            
        Returns:
            Correction ID
        """
        with self._lock:
            self._operation_count += 1
            
            correction_id = self.lifelong_learning.record_correction(
                mistake_id, correction_type, correction_data, success_rate, **kwargs
            )
            
            self.logger.log(LogLevel.INFO, "correction", f"Correction applied: {correction_type}", {
                "correction_id": correction_id,
                "mistake_id": mistake_id,
                "success_rate": success_rate
            })
            
            return correction_id
    
    def record_model_update(self, 
                           update_type: UpdateType,
                           description: str,
                           parameters_changed: List[str],
                           performance_before: Dict[str, float],
                           performance_after: Dict[str, float],
                           **kwargs) -> str:
        """
        Record a model update.
        
        Args:
            update_type: Type of update
            description: Description of the update
            parameters_changed: List of changed parameters
            performance_before: Performance before update
            performance_after: Performance after update
            **kwargs: Additional parameters
            
        Returns:
            Update ID
        """
        with self._lock:
            self._operation_count += 1
            
            update_id = self.lifelong_learning.record_update(
                update_type, description, parameters_changed,
                performance_before, performance_after, **kwargs
            )
            
            # Monitor performance metrics for drift
            if self.drift_detector:
                for metric, value in performance_after.items():
                    if isinstance(value, (int, float)):
                        self.drift_detector.add_sample(f"performance_{metric}", value)
            
            self.logger.log(LogLevel.INFO, "model_update", f"Model update recorded: {update_type.value}", {
                "update_id": update_id,
                "description": description,
                "performance_change": {
                    k: performance_after.get(k, 0) - performance_before.get(k, 0)
                    for k in performance_before.keys()
                }
            })
            
            return update_id
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            self._operation_count += 1
            return self.cache.get(key)
    
    def cache_set(self, key: str, value: Any, **kwargs) -> bool:
        """Set value in cache."""
        with self._lock:
            self._operation_count += 1
            return self.cache.set(key, value, **kwargs)
    
    def add_hook(self, event: str, callback: Callable) -> None:
        """
        Add a hook for specific events.
        
        Args:
            event: Event name
            callback: Callback function
        """
        with self._lock:
            if event not in self._hooks:
                self._hooks[event] = []
            self._hooks[event].append(callback)
    
    def remove_hook(self, event: str, callback: Callable) -> None:
        """
        Remove a hook for specific events.
        
        Args:
            event: Event name
            callback: Callback function
        """
        with self._lock:
            if event in self._hooks and callback in self._hooks[event]:
                self._hooks[event].remove(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                "config": self.config.to_dict(),
                "cache_stats": self.cache.get_stats(),
                "replay_buffer_stats": self.replay_buffer.get_stats(),
                "lifelong_learning_stats": self.lifelong_learning.get_statistics(),
                "logger_stats": self.logger.get_statistics()
            })
            
            if self.drift_detector:
                stats["drift_detector_stats"] = self.drift_detector.get_statistics()
            
            return stats
    
    def save_state(self, path: Optional[str] = None) -> None:
        """
        Save the current state to disk.
        
        Args:
            path: Path to save state (uses default if not provided)
        """
        with self._lock:
            save_path = path or (Path(self.config.storage_dir) / f"{self.config.agent_id}_state.json")
            
            # Create directory if it doesn't exist
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save state
            state = {
                "config": self.config.to_dict(),
                "statistics": self._stats,
                "timestamp": time.time()
            }
            
            with open(save_path, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Save component states
            self.lifelong_learning.save()
            
            self.logger.log(LogLevel.INFO, "state_management", f"State saved to {save_path}")
    
    def load_state(self, path: Optional[str] = None) -> None:
        """
        Load state from disk.
        
        Args:
            path: Path to load state from (uses default if not provided)
        """
        with self._lock:
            load_path = path or (Path(self.config.storage_dir) / f"{self.config.agent_id}_state.json")
            
            if not Path(load_path).exists():
                self.logger.log(LogLevel.WARNING, "state_management", f"State file not found: {load_path}")
                return
            
            # Load state
            with open(load_path, 'r') as f:
                state = json.load(f)
            
            # Load component states
            self.lifelong_learning.load()
            
            self.logger.log(LogLevel.INFO, "state_management", f"State loaded from {load_path}")
    
    def shutdown(self) -> None:
        """Shutdown the agent and cleanup resources."""
        with self._lock:
            self._is_running = False
            
            # Save final state
            self.save_state()
            
            # Close logger
            self.logger.close()
            
            self.logger.log(LogLevel.INFO, "shutdown", "AgentBase shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
    
    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, '_is_running') and self._is_running:
            self.shutdown() 