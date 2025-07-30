"""
AgentBase - Open Source AI Agent Storage with Learning and Adaptation

A comprehensive storage solution for AI agents with advanced memory management,
experience replay, lifelong learning, and concept drift detection capabilities.
"""

__version__ = "0.2.0"
__author__ = "AgentBase Contributors"
__email__ = "hello@agentbase.org"

from .core.agent_base import AgentBase
from .memory.cache import MemoryCache
from .memory.replay_buffer import ExperienceReplayBuffer
from .memory.lifelong_learning import LifelongLearningStore
from .logging.metadata_logger import MetadataLogger
from .drift.concept_drift import ConceptDriftDetector

__all__ = [
    "AgentBase",
    "MemoryCache",
    "ExperienceReplayBuffer",
    "LifelongLearningStore",
    "MetadataLogger",
    "ConceptDriftDetector",
] 