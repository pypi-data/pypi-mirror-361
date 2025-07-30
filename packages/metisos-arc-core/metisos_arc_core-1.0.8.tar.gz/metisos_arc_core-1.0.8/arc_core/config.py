"""ARC Core Configuration System

Configuration management for ARC Core with biological learning parameters.
"""

import os
import json
from typing import Dict, Any, Optional

class ARCConfig:
    """
    Main configuration class for ARC Core.
    
    Manages all configuration parameters for the ARC system including:
    - Model parameters (learning rate, model name, etc.)
    - Biological learning system parameters
    - Memory system configuration
    - Safety and inhibition thresholds
    - Reasoning graph parameters
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize ARC configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Core model parameters
        self.model_name = "cognitivecomputations/TinyDolphin-2.8-1.1b"
        self.learning_rate = 1e-4
        self.device = "auto"  # auto, cpu, cuda
        self.continue_learning = True
        self.model_save_dir = "arc_models"
        
        # LoRA configuration
        self.lora_rank = 16
        self.lora_alpha = 32
        self.lora_dropout = 0.1
        self.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        
        # Generation parameters
        self.temperature = 0.8
        self.top_p = 0.9
        self.max_new_tokens = 100
        self.repetition_penalty = 1.1
        
        # Learning parameters
        self.confidence_threshold = 0.3
        self.learning_frequency = 0.7
        self.novelty_bonus = 0.2
        self.ewc_lambda = 0.4  # Elastic Weight Consolidation
        
        # Biological learning parameters
        self.biological_learning = {
            "contextual_gating": {
                "novel_information_weight": 0.8,
                "relevant_to_goal_weight": 0.9,
                "social_interaction_weight": 0.7,
                "self_generated_weight": 0.3,
                "repetitive_weight": 0.2,
                "encoding_threshold": 0.6
            },
            "cognitive_inhibition": {
                "off_topic_inhibition": 0.9,
                "repetitive_inhibition": 0.8,
                "inappropriate_context_inhibition": 0.9,
                "low_quality_inhibition": 0.7
            },
            "sleep_consolidation": {
                "consolidation_interval": 50,
                "consolidation_throttle_seconds": 300
            },
            "metacognitive_monitoring": {
                "relevance_threshold": 0.7,
                "appropriateness_threshold": 0.8,
                "coherence_threshold": 0.6,
                "novelty_threshold": 0.3,
                "ai_obsession_threshold": 0.9
            }
        }
        
        # Memory system parameters
        self.memory = {
            "working_memory_size": 7,
            "episodic_memory_size": 1000,
            "semantic_memory_enabled": True,
            "hierarchical_enabled": True
        }
        
        # Reasoning graph parameters
        self.reasoning_graph = {
            "max_concepts": 10000,
            "max_relationships": 50000,
            "causal_strength_threshold": 0.3,
            "reasoning_depth": 4,
            "pattern_learning_enabled": True
        }
        
        # Safety parameters
        self.safety = {
            "content_filtering_enabled": True,
            "bias_detection_enabled": True,
            "inappropriate_response_threshold": 0.8,
            "safety_monitoring_enabled": True
        }
        
        # Vocabulary learning parameters
        self.vocabulary = {
            "novel_concept_detection": True,
            "concept_validation_strict": True,
            "min_concept_length": 3,
            "max_concept_length": 30,
            "learning_enabled": True
        }
        
        # Load from file if provided
        if config_path:
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: str):
        """Load configuration from JSON file."""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                self._update_from_dict(config_data)
                print(f"Configuration loaded from {config_path}")
            except Exception as e:
                print(f"Failed to load config from {config_path}: {e}")
        else:
            print(f"Config file not found: {config_path}")
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file."""
        try:
            config_data = self.to_dict()
            # Only create directory if dirname is not empty
            dirname = os.path.dirname(config_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"Configuration saved to {config_path}")
        except Exception as e:
            print(f"Failed to save config to {config_path}: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_data.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), dict) and isinstance(value, dict):
                    # Deep merge for nested dicts
                    getattr(self, key).update(value)
                else:
                    setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "model_name": self.model_name,
            "learning_rate": self.learning_rate,
            "device": self.device,
            "continue_learning": self.continue_learning,
            "model_save_dir": self.model_save_dir,
            "lora_rank": self.lora_rank,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
            "target_modules": self.target_modules,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_new_tokens": self.max_new_tokens,
            "repetition_penalty": self.repetition_penalty,
            "confidence_threshold": self.confidence_threshold,
            "learning_frequency": self.learning_frequency,
            "novelty_bonus": self.novelty_bonus,
            "ewc_lambda": self.ewc_lambda,
            "biological_learning": self.biological_learning,
            "memory": self.memory,
            "reasoning_graph": self.reasoning_graph,
            "safety": self.safety,
            "vocabulary": self.vocabulary
        }
    
    def get_lora_config(self):
        """Get LoRA configuration for PEFT."""
        from peft import LoraConfig, TaskType
        return LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=self.lora_rank,
            lora_alpha=self.lora_alpha,
            lora_dropout=self.lora_dropout,
            target_modules=self.target_modules
        )
    
    def get_generation_config(self):
        """Get generation configuration for transformers."""
        from transformers import GenerationConfig
        return GenerationConfig(
            do_sample=True,
            temperature=self.temperature,
            top_p=self.top_p,
            max_new_tokens=self.max_new_tokens,
            repetition_penalty=self.repetition_penalty
        )
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        errors = []
        
        # Check learning rate
        if not 0 < self.learning_rate < 1:
            errors.append(f"Invalid learning_rate: {self.learning_rate}")
        
        # Check LoRA parameters
        if not 1 <= self.lora_rank <= 128:
            errors.append(f"Invalid lora_rank: {self.lora_rank}")
        
        # Check temperature
        if not 0 < self.temperature <= 2.0:
            errors.append(f"Invalid temperature: {self.temperature}")
        
        # Check thresholds
        if not 0 <= self.confidence_threshold <= 1:
            errors.append(f"Invalid confidence_threshold: {self.confidence_threshold}")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True

def create_default_config() -> ARCConfig:
    """Create default ARC configuration."""
    return ARCConfig()

def load_config_from_file(config_path: str) -> ARCConfig:
    """Load ARC configuration from file."""
    return ARCConfig(config_path)

def create_minimal_config() -> ARCConfig:
    """Create minimal configuration for testing/lightweight usage."""
    config = ARCConfig()
    
    # Reduce memory usage
    config.lora_rank = 8
    config.max_new_tokens = 50
    config.memory["working_memory_size"] = 5
    config.memory["episodic_memory_size"] = 100
    config.biological_learning["sleep_consolidation"]["consolidation_interval"] = 25
    
    return config
