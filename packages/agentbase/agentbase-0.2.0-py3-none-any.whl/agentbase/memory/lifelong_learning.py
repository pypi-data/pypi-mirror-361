"""
Lifelong Learning Store - Keep track of model updates, mistakes, and corrections.

This module provides a comprehensive storage system for tracking learning progress,
model evolution, and error patterns for continuous improvement.
"""

import json
import threading
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import pickle
import gzip
import os


class UpdateType(Enum):
    """Types of model updates."""
    GRADIENT_UPDATE = "gradient_update"
    PARAMETER_UPDATE = "parameter_update"
    ARCHITECTURE_CHANGE = "architecture_change"
    HYPERPARAMETER_CHANGE = "hyperparameter_change"
    KNOWLEDGE_UPDATE = "knowledge_update"
    ERROR_CORRECTION = "error_correction"


class MistakeType(Enum):
    """Types of mistakes/errors."""
    PREDICTION_ERROR = "prediction_error"
    CLASSIFICATION_ERROR = "classification_error"
    REGRESSION_ERROR = "regression_error"
    REASONING_ERROR = "reasoning_error"
    FACTUAL_ERROR = "factual_error"
    TEMPORAL_ERROR = "temporal_error"
    CAUSAL_ERROR = "causal_error"


@dataclass
class ModelUpdate:
    """
    Record of a model update.
    """
    update_id: str
    update_type: UpdateType
    timestamp: float
    description: str
    parameters_changed: List[str]
    performance_before: Dict[str, float]
    performance_after: Dict[str, float]
    update_data: Dict[str, Any]
    validation_score: Optional[float] = None
    rollback_available: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["update_type"] = self.update_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelUpdate':
        """Create from dictionary."""
        data["update_type"] = UpdateType(data["update_type"])
        return cls(**data)


@dataclass
class Mistake:
    """
    Record of a mistake/error made by the agent.
    """
    mistake_id: str
    mistake_type: MistakeType
    timestamp: float
    context: Dict[str, Any]
    expected_output: Any
    actual_output: Any
    error_magnitude: float
    input_data: Any
    correction_applied: bool = False
    correction_id: Optional[str] = None
    learning_opportunity: bool = True
    severity: str = "medium"  # low, medium, high, critical
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["mistake_type"] = self.mistake_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mistake':
        """Create from dictionary."""
        data["mistake_type"] = MistakeType(data["mistake_type"])
        return cls(**data)


@dataclass
class Correction:
    """
    Record of a correction applied to fix a mistake.
    """
    correction_id: str
    mistake_id: str
    timestamp: float
    correction_type: str
    correction_data: Dict[str, Any]
    success_rate: float
    validation_results: Dict[str, Any]
    follow_up_required: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Correction':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class LearningSession:
    """
    Record of a learning session.
    """
    session_id: str
    start_time: float
    end_time: Optional[float]
    task_type: str
    learning_objective: str
    initial_performance: Dict[str, float]
    final_performance: Dict[str, float]
    updates_applied: List[str]
    mistakes_made: List[str]
    corrections_applied: List[str]
    knowledge_gained: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningSession':
        """Create from dictionary."""
        return cls(**data)


class LifelongLearningStore:
    """
    Comprehensive storage system for lifelong learning.
    
    Features:
    - Track model updates and changes
    - Record mistakes and error patterns
    - Store corrections and their effectiveness
    - Manage learning sessions
    - Analyze learning progress
    - Detect recurring patterns
    - Support for rollback and recovery
    """
    
    def __init__(self, 
                 max_updates: int = 10000,
                 max_mistakes: int = 50000,
                 max_corrections: int = 25000,
                 max_sessions: int = 1000,
                 save_path: Optional[str] = None,
                 auto_save_interval: int = 100):
        """
        Initialize the lifelong learning store.
        
        Args:
            max_updates: Maximum number of model updates to store
            max_mistakes: Maximum number of mistakes to store
            max_corrections: Maximum number of corrections to store
            max_sessions: Maximum number of learning sessions to store
            save_path: Path to save data to disk
            auto_save_interval: Auto-save every N operations
        """
        self.max_updates = max_updates
        self.max_mistakes = max_mistakes
        self.max_corrections = max_corrections
        self.max_sessions = max_sessions
        self.save_path = save_path
        self.auto_save_interval = auto_save_interval
        
        # Storage
        self._updates: deque = deque(maxlen=max_updates)
        self._mistakes: deque = deque(maxlen=max_mistakes)
        self._corrections: deque = deque(maxlen=max_corrections)
        self._sessions: deque = deque(maxlen=max_sessions)
        
        # Indexes for fast lookup
        self._update_index: Dict[str, ModelUpdate] = {}
        self._mistake_index: Dict[str, Mistake] = {}
        self._correction_index: Dict[str, Correction] = {}
        self._session_index: Dict[str, LearningSession] = {}
        
        # Pattern tracking
        self._mistake_patterns: Dict[str, List[str]] = defaultdict(list)
        self._correction_effectiveness: Dict[str, List[float]] = defaultdict(list)
        self._learning_trends: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            "total_updates": 0,
            "total_mistakes": 0,
            "total_corrections": 0,
            "total_sessions": 0,
            "correction_success_rate": 0.0,
            "learning_velocity": 0.0,
        }
        
        # Current session
        self._current_session: Optional[LearningSession] = None
        
        # Auto-save counter
        self._save_counter = 0
    
    def record_update(self, 
                     update_type: UpdateType,
                     description: str,
                     parameters_changed: List[str],
                     performance_before: Dict[str, float],
                     performance_after: Dict[str, float],
                     update_data: Dict[str, Any],
                     validation_score: Optional[float] = None,
                     rollback_available: bool = False,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a model update.
        
        Args:
            update_type: Type of update
            description: Description of the update
            parameters_changed: List of parameter names changed
            performance_before: Performance metrics before update
            performance_after: Performance metrics after update
            update_data: Data about the update
            validation_score: Validation score if available
            rollback_available: Whether rollback is possible
            metadata: Additional metadata
            
        Returns:
            Update ID
        """
        with self._lock:
            # Generate unique ID
            update_id = self._generate_id("update")
            
            # Create update record
            update = ModelUpdate(
                update_id=update_id,
                update_type=update_type,
                timestamp=time.time(),
                description=description,
                parameters_changed=parameters_changed,
                performance_before=performance_before,
                performance_after=performance_after,
                update_data=update_data,
                validation_score=validation_score,
                rollback_available=rollback_available,
                metadata=metadata
            )
            
            # Store update
            self._updates.append(update)
            self._update_index[update_id] = update
            
            # Update statistics
            self._stats["total_updates"] += 1
            
            # Track learning trends
            for metric, value in performance_after.items():
                self._learning_trends[metric].append((time.time(), value))
            
            # Add to current session if active
            if self._current_session:
                self._current_session.updates_applied.append(update_id)
            
            # Auto-save
            self._maybe_auto_save()
            
            return update_id
    
    def record_mistake(self,
                      mistake_type: MistakeType,
                      context: Dict[str, Any],
                      expected_output: Any,
                      actual_output: Any,
                      error_magnitude: float,
                      input_data: Any,
                      severity: str = "medium",
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a mistake made by the agent.
        
        Args:
            mistake_type: Type of mistake
            context: Context in which mistake occurred
            expected_output: What the output should have been
            actual_output: What the output actually was
            error_magnitude: Magnitude of the error
            input_data: Input data that led to the mistake
            severity: Severity level (low, medium, high, critical)
            metadata: Additional metadata
            
        Returns:
            Mistake ID
        """
        with self._lock:
            # Generate unique ID
            mistake_id = self._generate_id("mistake")
            
            # Create mistake record
            mistake = Mistake(
                mistake_id=mistake_id,
                mistake_type=mistake_type,
                timestamp=time.time(),
                context=context,
                expected_output=expected_output,
                actual_output=actual_output,
                error_magnitude=error_magnitude,
                input_data=input_data,
                severity=severity,
                metadata=metadata
            )
            
            # Store mistake
            self._mistakes.append(mistake)
            self._mistake_index[mistake_id] = mistake
            
            # Update statistics
            self._stats["total_mistakes"] += 1
            
            # Track mistake patterns
            pattern_key = f"{mistake_type.value}_{severity}"
            self._mistake_patterns[pattern_key].append(mistake_id)
            
            # Add to current session if active
            if self._current_session:
                self._current_session.mistakes_made.append(mistake_id)
            
            # Auto-save
            self._maybe_auto_save()
            
            return mistake_id
    
    def record_correction(self,
                         mistake_id: str,
                         correction_type: str,
                         correction_data: Dict[str, Any],
                         success_rate: float,
                         validation_results: Dict[str, Any],
                         follow_up_required: bool = False,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a correction applied to fix a mistake.
        
        Args:
            mistake_id: ID of the mistake being corrected
            correction_type: Type of correction
            correction_data: Data about the correction
            success_rate: Success rate of the correction
            validation_results: Results of validation
            follow_up_required: Whether follow-up is needed
            metadata: Additional metadata
            
        Returns:
            Correction ID
        """
        with self._lock:
            # Generate unique ID
            correction_id = self._generate_id("correction")
            
            # Create correction record
            correction = Correction(
                correction_id=correction_id,
                mistake_id=mistake_id,
                timestamp=time.time(),
                correction_type=correction_type,
                correction_data=correction_data,
                success_rate=success_rate,
                validation_results=validation_results,
                follow_up_required=follow_up_required,
                metadata=metadata
            )
            
            # Store correction
            self._corrections.append(correction)
            self._correction_index[correction_id] = correction
            
            # Update mistake record
            if mistake_id in self._mistake_index:
                mistake = self._mistake_index[mistake_id]
                mistake.correction_applied = True
                mistake.correction_id = correction_id
            
            # Update statistics
            self._stats["total_corrections"] += 1
            
            # Track correction effectiveness
            self._correction_effectiveness[correction_type].append(success_rate)
            
            # Update overall success rate
            all_rates = []
            for rates in self._correction_effectiveness.values():
                all_rates.extend(rates)
            self._stats["correction_success_rate"] = sum(all_rates) / len(all_rates) if all_rates else 0.0
            
            # Add to current session if active
            if self._current_session:
                self._current_session.corrections_applied.append(correction_id)
            
            # Auto-save
            self._maybe_auto_save()
            
            return correction_id
    
    def start_learning_session(self,
                              task_type: str,
                              learning_objective: str,
                              initial_performance: Dict[str, float],
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new learning session.
        
        Args:
            task_type: Type of task being learned
            learning_objective: Objective of the learning session
            initial_performance: Initial performance metrics
            metadata: Additional metadata
            
        Returns:
            Session ID
        """
        with self._lock:
            # End current session if active
            if self._current_session:
                self.end_learning_session()
            
            # Generate unique ID
            session_id = self._generate_id("session")
            
            # Create session record
            session = LearningSession(
                session_id=session_id,
                start_time=time.time(),
                end_time=None,
                task_type=task_type,
                learning_objective=learning_objective,
                initial_performance=initial_performance,
                final_performance={},
                updates_applied=[],
                mistakes_made=[],
                corrections_applied=[],
                knowledge_gained={},
                metadata=metadata
            )
            
            # Set as current session
            self._current_session = session
            
            return session_id
    
    def end_learning_session(self,
                            final_performance: Optional[Dict[str, float]] = None,
                            knowledge_gained: Optional[Dict[str, Any]] = None) -> None:
        """
        End the current learning session.
        
        Args:
            final_performance: Final performance metrics
            knowledge_gained: Knowledge gained during session
        """
        with self._lock:
            if not self._current_session:
                return
            
            # Update session
            self._current_session.end_time = time.time()
            if final_performance:
                self._current_session.final_performance = final_performance
            if knowledge_gained:
                self._current_session.knowledge_gained = knowledge_gained
            
            # Store session
            self._sessions.append(self._current_session)
            self._session_index[self._current_session.session_id] = self._current_session
            
            # Update statistics
            self._stats["total_sessions"] += 1
            
            # Calculate learning velocity
            if self._current_session.final_performance and self._current_session.initial_performance:
                session_duration = self._current_session.end_time - self._current_session.start_time
                if session_duration > 0:
                    improvement = sum(
                        self._current_session.final_performance.get(k, 0) - 
                        self._current_session.initial_performance.get(k, 0)
                        for k in self._current_session.initial_performance.keys()
                    )
                    velocity = improvement / session_duration
                    self._stats["learning_velocity"] = velocity
            
            # Clear current session
            self._current_session = None
            
            # Auto-save
            self._maybe_auto_save()
    
    def get_mistake_patterns(self) -> Dict[str, List[str]]:
        """Get mistake patterns."""
        with self._lock:
            return dict(self._mistake_patterns)
    
    def get_correction_effectiveness(self) -> Dict[str, float]:
        """Get correction effectiveness by type."""
        with self._lock:
            return {
                correction_type: sum(rates) / len(rates) if rates else 0.0
                for correction_type, rates in self._correction_effectiveness.items()
            }
    
    def get_learning_trends(self) -> Dict[str, List[Tuple[float, float]]]:
        """Get learning trends over time."""
        with self._lock:
            return dict(self._learning_trends)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        with self._lock:
            return self._stats.copy()
    
    def analyze_recurring_mistakes(self, window_size: int = 100) -> Dict[str, int]:
        """
        Analyze recurring mistakes in recent history.
        
        Args:
            window_size: Size of the analysis window
            
        Returns:
            Dictionary of mistake types and their frequencies
        """
        with self._lock:
            recent_mistakes = list(self._mistakes)[-window_size:]
            mistake_counts = defaultdict(int)
            
            for mistake in recent_mistakes:
                mistake_counts[mistake.mistake_type.value] += 1
            
            return dict(mistake_counts)
    
    def get_rollback_candidates(self) -> List[ModelUpdate]:
        """Get updates that can be rolled back."""
        with self._lock:
            return [update for update in self._updates if update.rollback_available]
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save the store to disk.
        
        Args:
            path: Path to save to (uses default if not provided)
        """
        with self._lock:
            save_path = path or self.save_path
            if not save_path:
                return
            
            data = {
                "updates": [update.to_dict() for update in self._updates],
                "mistakes": [mistake.to_dict() for mistake in self._mistakes],
                "corrections": [correction.to_dict() for correction in self._corrections],
                "sessions": [session.to_dict() for session in self._sessions],
                "stats": self._stats,
                "patterns": dict(self._mistake_patterns),
                "effectiveness": dict(self._correction_effectiveness),
                "trends": dict(self._learning_trends),
            }
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with gzip.open(save_path, 'wb') as f:
                pickle.dump(data, f)
    
    def load(self, path: Optional[str] = None) -> None:
        """
        Load the store from disk.
        
        Args:
            path: Path to load from (uses default if not provided)
        """
        with self._lock:
            load_path = path or self.save_path
            if not load_path or not os.path.exists(load_path):
                return
            
            with gzip.open(load_path, 'rb') as f:
                data = pickle.load(f)
            
            # Restore data
            self._updates = deque([ModelUpdate.from_dict(u) for u in data["updates"]], 
                                maxlen=self.max_updates)
            self._mistakes = deque([Mistake.from_dict(m) for m in data["mistakes"]], 
                                maxlen=self.max_mistakes)
            self._corrections = deque([Correction.from_dict(c) for c in data["corrections"]], 
                                    maxlen=self.max_corrections)
            self._sessions = deque([LearningSession.from_dict(s) for s in data["sessions"]], 
                                maxlen=self.max_sessions)
            
            # Rebuild indexes
            self._update_index = {u.update_id: u for u in self._updates}
            self._mistake_index = {m.mistake_id: m for m in self._mistakes}
            self._correction_index = {c.correction_id: c for c in self._corrections}
            self._session_index = {s.session_id: s for s in self._sessions}
            
            # Restore patterns and stats
            self._stats = data["stats"]
            self._mistake_patterns = defaultdict(list, data["patterns"])
            self._correction_effectiveness = defaultdict(list, data["effectiveness"])
            self._learning_trends = defaultdict(list, data["trends"])
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        return f"{prefix}_{int(time.time() * 1000000)}"
    
    def _maybe_auto_save(self) -> None:
        """Auto-save if counter reached."""
        self._save_counter += 1
        if self.save_path and self._save_counter >= self.auto_save_interval:
            self._save_counter = 0
            self.save()
    
    def __len__(self) -> int:
        """Get total number of stored records."""
        with self._lock:
            return len(self._updates) + len(self._mistakes) + len(self._corrections) + len(self._sessions) 