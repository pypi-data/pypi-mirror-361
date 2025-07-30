"""
SE-AGI: Self-Evolving General AI
The Holy Grail of Autonomous Intelligence

A revolutionary modular AI system capable of autonomous learning,
adaptation, and intelligence evolution.
"""

from .__version__ import __version__, __version_info__, RELEASE_STAGE

__author__ = "Krishna Bajpai"
__email__ = "bajpaikrishna715@gmail.com"

from .core.seagi import SEAGI
from .core.config import AgentConfig, SEAGIConfig
from .core.meta_learner import MetaLearner
from .core.reflection import ReflectionEngine
from .agents.base import BaseAgent
from .agents.meta_agent import MetaAgent
from .agents.research_agent import ResearchAgent
from .agents.creative_agent import CreativeAgent
from .agents.analysis_agent import AnalysisAgent
from .agents.tool_agent import ToolAgent
from .reasoning.multimodal import MultiModalReasoner
from .memory.episodic import EpisodicMemory
from .memory.semantic import SemanticMemory
from .evolution.capability_evolution import CapabilityEvolver
from .safety.monitor import SafetyMonitor
from .safety.alignment import AlignmentChecker

# Core components for easy access
__all__ = [
    "SEAGI",
    "AgentConfig", 
    "SEAGIConfig",
    "MetaLearner",
    "ReflectionEngine",
    "BaseAgent",
    "MetaAgent",
    "ResearchAgent",
    "CreativeAgent", 
    "AnalysisAgent",
    "ToolAgent",
    "MultiModalReasoner",
    "EpisodicMemory",
    "SemanticMemory",
    "CapabilityEvolver",
    "SafetyMonitor",
    "AlignmentChecker",
]

# Version info
VERSION = __version__
