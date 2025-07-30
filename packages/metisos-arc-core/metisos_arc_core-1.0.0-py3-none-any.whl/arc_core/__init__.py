"""
ARC Core - Adaptive Recursive Consciousness

A complete implementation of biological learning mechanisms for AI systems.
"""

__version__ = "1.0.0"

# Core configuration system
from .config import ARCConfig, create_default_config

# Complete training system with LoRA neural learning
from .train import ARCTrainer, LearningARCTransformer

# Complete memory system with biological learning mechanisms
from .memory import (
    MemorySystem,
    HierarchicalMemory,
    BiologicalContextualGating,
    SleepLikeConsolidation,
    MultipleLearningSystems
)

# Complete safety system with cognitive inhibition and metacognitive monitoring
from .safety import (
    SafetySystem,
    CognitiveInhibition,
    MetacognitiveMonitoring
)

# Export all public classes and functions
__all__ = [
    # Core classes
    'ARCConfig',
    'create_default_config',
    'ARCTrainer',
    'MemorySystem',
    'SafetySystem',
    
    # Neural learning components
    'LearningARCTransformer',
    
    # Memory system components
    'HierarchicalMemory',
    'BiologicalContextualGating',
    'SleepLikeConsolidation',
    'MultipleLearningSystems',
    
    # Safety system components
    'CognitiveInhibition',
    'MetacognitiveMonitoring',
    
    # Package metadata
    '__version__'
]
