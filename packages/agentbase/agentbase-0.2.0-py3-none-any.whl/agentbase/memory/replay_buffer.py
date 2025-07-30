"""
Experience Replay Buffer - Store past interactions for reinforcement learning.

This module provides a comprehensive experience replay buffer implementation
with various sampling strategies and efficient storage mechanisms.
"""

import random
import numpy as np
import threading
from collections import deque, namedtuple
from typing import Any, Dict, List, Optional, Tuple, Union, Iterator
import pickle
import gzip
import os
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


@dataclass
class Experience:
    """
    A single experience/transition in the replay buffer.
    """
    state: Any
    action: Any
    reward: float
    next_state: Any
    done: bool
    priority: float = 1.0
    timestamp: float = 0.0
    episode_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert experience to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experience':
        """Create experience from dictionary."""
        return cls(**data)


class SamplingStrategy(ABC):
    """Abstract base class for sampling strategies."""
    
    @abstractmethod
    def sample(self, buffer: List[Experience], batch_size: int) -> List[int]:
        """Sample indices from the buffer."""
        pass


class UniformSampling(SamplingStrategy):
    """Uniform random sampling strategy."""
    
    def sample(self, buffer: List[Experience], batch_size: int) -> List[int]:
        """Sample uniformly random indices."""
        return random.sample(range(len(buffer)), min(batch_size, len(buffer)))


class PrioritizedSampling(SamplingStrategy):
    """Prioritized experience replay sampling."""
    
    def __init__(self, alpha: float = 0.6, beta: float = 0.4, beta_increment: float = 0.001):
        """
        Initialize prioritized sampling.
        
        Args:
            alpha: Prioritization exponent (0 = uniform, 1 = fully prioritized)
            beta: Importance sampling correction exponent
            beta_increment: Beta increment per sample
        """
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.max_priority = 1.0
    
    def sample(self, buffer: List[Experience], batch_size: int) -> List[int]:
        """Sample based on priorities."""
        if not buffer:
            return []
        
        # Get priorities
        priorities = np.array([exp.priority for exp in buffer])
        priorities = np.power(priorities, self.alpha)
        
        # Calculate probabilities
        probabilities = priorities / np.sum(priorities)
        
        # Sample indices
        indices = np.random.choice(len(buffer), size=min(batch_size, len(buffer)), 
                                 p=probabilities, replace=False)
        
        # Update beta
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        return indices.tolist()


class RecentSampling(SamplingStrategy):
    """Sample more recent experiences with higher probability."""
    
    def __init__(self, recency_weight: float = 0.8):
        """
        Initialize recent sampling.
        
        Args:
            recency_weight: Weight for recent experiences (0-1)
        """
        self.recency_weight = recency_weight
    
    def sample(self, buffer: List[Experience], batch_size: int) -> List[int]:
        """Sample with recency bias."""
        if not buffer:
            return []
        
        # Create weights based on recency
        weights = np.array([self.recency_weight ** (len(buffer) - i - 1) 
                          for i in range(len(buffer))])
        weights = weights / np.sum(weights)
        
        # Sample indices
        indices = np.random.choice(len(buffer), size=min(batch_size, len(buffer)), 
                                 p=weights, replace=False)
        
        return indices.tolist()


class ExperienceReplayBuffer:
    """
    Comprehensive experience replay buffer for reinforcement learning.
    
    Features:
    - Multiple sampling strategies (uniform, prioritized, recent)
    - Efficient storage with circular buffer
    - Thread-safe operations
    - Persistence support
    - Episode tracking
    - Statistics and monitoring
    - Memory management
    """
    
    def __init__(self, 
                 capacity: int = 100000,
                 sampling_strategy: str = "uniform",
                 alpha: float = 0.6,
                 beta: float = 0.4,
                 beta_increment: float = 0.001,
                 min_size_to_sample: int = 1000,
                 save_path: Optional[str] = None,
                 auto_save_interval: int = 1000):
        """
        Initialize the experience replay buffer.
        
        Args:
            capacity: Maximum number of experiences to store
            sampling_strategy: Sampling strategy ("uniform", "prioritized", "recent")
            alpha: Prioritization exponent for prioritized sampling
            beta: Importance sampling correction exponent
            beta_increment: Beta increment per sample
            min_size_to_sample: Minimum buffer size before sampling
            save_path: Path to save buffer to disk
            auto_save_interval: Auto-save every N experiences
        """
        self.capacity = capacity
        self.min_size_to_sample = min_size_to_sample
        self.save_path = save_path
        self.auto_save_interval = auto_save_interval
        
        # Storage
        self._buffer: List[Experience] = []
        self._position = 0
        self._lock = threading.RLock()
        
        # Sampling strategy
        self._setup_sampling_strategy(sampling_strategy, alpha, beta, beta_increment)
        
        # Episode tracking
        self._current_episode_id: Optional[str] = None
        self._episodes: Dict[str, List[int]] = {}
        
        # Statistics
        self._stats = {
            "total_added": 0,
            "total_sampled": 0,
            "episodes_completed": 0,
            "average_episode_length": 0.0,
            "total_reward": 0.0,
            "average_reward": 0.0,
        }
        
        # Auto-save counter
        self._save_counter = 0
    
    def _setup_sampling_strategy(self, strategy: str, alpha: float, beta: float, beta_increment: float):
        """Setup the sampling strategy."""
        if strategy == "uniform":
            self._sampling_strategy = UniformSampling()
        elif strategy == "prioritized":
            self._sampling_strategy = PrioritizedSampling(alpha, beta, beta_increment)
        elif strategy == "recent":
            self._sampling_strategy = RecentSampling()
        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")
    
    def add(self, 
            state: Any,
            action: Any,
            reward: float,
            next_state: Any,
            done: bool,
            priority: float = 1.0,
            episode_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new experience to the buffer.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
            priority: Priority for prioritized sampling
            episode_id: Episode identifier
            metadata: Additional metadata
        """
        with self._lock:
            import time
            
            # Create experience
            experience = Experience(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=done,
                priority=priority,
                timestamp=time.time(),
                episode_id=episode_id,
                metadata=metadata
            )
            
            # Add to buffer
            if len(self._buffer) < self.capacity:
                self._buffer.append(experience)
            else:
                # Remove old episode tracking if overwriting
                old_exp = self._buffer[self._position]
                if old_exp.episode_id and old_exp.episode_id in self._episodes:
                    self._episodes[old_exp.episode_id].remove(self._position)
                    if not self._episodes[old_exp.episode_id]:
                        del self._episodes[old_exp.episode_id]
                
                # Overwrite old experience
                self._buffer[self._position] = experience
            
            # Update episode tracking
            if episode_id:
                if episode_id not in self._episodes:
                    self._episodes[episode_id] = []
                self._episodes[episode_id].append(self._position)
            
            # Update position
            self._position = (self._position + 1) % self.capacity
            
            # Update statistics
            self._stats["total_added"] += 1
            self._stats["total_reward"] += reward
            self._stats["average_reward"] = self._stats["total_reward"] / self._stats["total_added"]
            
            if done:
                self._stats["episodes_completed"] += 1
                if episode_id and episode_id in self._episodes:
                    episode_length = len(self._episodes[episode_id])
                    self._stats["average_episode_length"] = (
                        (self._stats["average_episode_length"] * (self._stats["episodes_completed"] - 1) + episode_length) /
                        self._stats["episodes_completed"]
                    )
            
            # Auto-save
            self._save_counter += 1
            if self.save_path and self._save_counter >= self.auto_save_interval:
                self._save_counter = 0
                self.save(self.save_path)
    
    def sample(self, batch_size: int) -> Optional[List[Experience]]:
        """
        Sample a batch of experiences.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of sampled experiences or None if buffer too small
        """
        with self._lock:
            if len(self._buffer) < self.min_size_to_sample:
                return None
            
            # Sample indices
            indices = self._sampling_strategy.sample(self._buffer, batch_size)
            
            # Get experiences
            experiences = [self._buffer[i] for i in indices]
            
            # Update statistics
            self._stats["total_sampled"] += len(experiences)
            
            return experiences
    
    def sample_episode(self, episode_id: str) -> Optional[List[Experience]]:
        """
        Sample all experiences from a specific episode.
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            List of experiences from the episode or None if not found
        """
        with self._lock:
            if episode_id not in self._episodes:
                return None
            
            indices = self._episodes[episode_id]
            return [self._buffer[i] for i in indices]
    
    def update_priorities(self, indices: List[int], priorities: List[float]) -> None:
        """
        Update priorities for prioritized sampling.
        
        Args:
            indices: Indices of experiences to update
            priorities: New priorities
        """
        with self._lock:
            if not isinstance(self._sampling_strategy, PrioritizedSampling):
                return
            
            for idx, priority in zip(indices, priorities):
                if 0 <= idx < len(self._buffer):
                    self._buffer[idx].priority = priority
                    self._sampling_strategy.max_priority = max(
                        self._sampling_strategy.max_priority, priority
                    )
    
    def clear(self) -> None:
        """Clear all experiences from the buffer."""
        with self._lock:
            self._buffer.clear()
            self._position = 0
            self._episodes.clear()
            self._stats = {
                "total_added": 0,
                "total_sampled": 0,
                "episodes_completed": 0,
                "average_episode_length": 0.0,
                "total_reward": 0.0,
                "average_reward": 0.0,
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        with self._lock:
            return {
                **self._stats,
                "current_size": len(self._buffer),
                "capacity": self.capacity,
                "fill_percentage": (len(self._buffer) / self.capacity) * 100,
                "total_episodes": len(self._episodes),
                "sampling_strategy": type(self._sampling_strategy).__name__,
            }
    
    def get_episode_ids(self) -> List[str]:
        """Get all episode IDs."""
        with self._lock:
            return list(self._episodes.keys())
    
    def get_episode_length(self, episode_id: str) -> int:
        """Get the length of a specific episode."""
        with self._lock:
            return len(self._episodes.get(episode_id, []))
    
    def save(self, path: str) -> None:
        """
        Save the buffer to disk.
        
        Args:
            path: Path to save the buffer
        """
        with self._lock:
            data = {
                "buffer": self._buffer,
                "position": self._position,
                "episodes": self._episodes,
                "stats": self._stats,
                "capacity": self.capacity,
            }
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with gzip.open(path, 'wb') as f:
                pickle.dump(data, f)
    
    def load(self, path: str) -> None:
        """
        Load the buffer from disk.
        
        Args:
            path: Path to load the buffer from
        """
        with self._lock:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Buffer file not found: {path}")
            
            with gzip.open(path, 'rb') as f:
                data = pickle.load(f)
            
            self._buffer = data["buffer"]
            self._position = data["position"]
            self._episodes = data["episodes"]
            self._stats = data["stats"]
            self.capacity = data["capacity"]
    
    def __len__(self) -> int:
        """Get the current size of the buffer."""
        with self._lock:
            return len(self._buffer)
    
    def __getitem__(self, index: int) -> Experience:
        """Get an experience by index."""
        with self._lock:
            return self._buffer[index]
    
    def __iter__(self) -> Iterator[Experience]:
        """Iterate over all experiences."""
        with self._lock:
            return iter(self._buffer.copy())
    
    def is_ready(self) -> bool:
        """Check if buffer is ready for sampling."""
        return len(self._buffer) >= self.min_size_to_sample 