"""
ARC Core Training Interface

This module provides the public API for ARC training functionality.
The actual implementation is provided via the PyPI package installation.

Install: pip install metisos-arc-core
"""

import os
import json
import time
import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from datasets import Dataset
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict, deque
import threading
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearningARCTransformer:
    """Core neural learning with LoRA adapters and real weight updates."""
    
    def __init__(self, model_name="cognitivecomputations/TinyDolphin-2.8-1.1b", config=None):
        """Initialize learning transformer with LoRA adapters."""
        self.model_name = model_name
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Learning configuration
        if config and hasattr(config, 'lora'):
            self.lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=config.lora.get('r', 8),
                lora_alpha=config.lora.get('lora_alpha', 32),
                lora_dropout=config.lora.get('lora_dropout', 0.1),
                target_modules=config.lora.get('target_modules', ["q_proj", "v_proj"])
            )
            self.learning_rate = config.model.get('learning_rate', 1e-4)
        else:
            # Determine target modules based on model architecture
            target_modules = self._get_target_modules_for_model(model_name)
            
            self.lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=8,
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=target_modules
            )
            self.learning_rate = 1e-4
        
        # Initialize model components
        self.tokenizer = None
        self.model = None
        self.optimizer = None
        
        # Learning tracking
        self.learning_history = deque(maxlen=1000)
        self.learning_stats = defaultdict(float)
        self.total_updates = 0
        
        # Thread safety
        self.learning_lock = threading.RLock()
    
    def _get_target_modules_for_model(self, model_name):
        """Determine appropriate target modules based on model architecture."""
        model_name_lower = model_name.lower()
        
        # GPT-2 and similar models
        if any(name in model_name_lower for name in ['gpt2', 'gpt-2', 'distilgpt2', 'dialogpt']):
            return ["c_attn", "c_proj"]
        
        # Llama-based models (including TinyDolphin)
        elif any(name in model_name_lower for name in ['llama', 'dolphin', 'alpaca', 'vicuna']):
            return ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        
        # BERT-based models
        elif any(name in model_name_lower for name in ['bert', 'roberta', 'electra']):
            return ["query", "value", "key"]
        
        # T5-based models
        elif 't5' in model_name_lower:
            return ["q", "v", "k", "o"]
        
        # Default to GPT-2 style for unknown models
        else:
            logger.warning(f"Unknown model architecture for {model_name}, using GPT-2 target modules")
            return ["c_attn", "c_proj"]
    
    def initialize_model(self):
        """Initialize the model with LoRA adapters."""
        logger.info(f"Initializing model: {self.model_name}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side='left'
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32,
                device_map="auto" if self.device.type == 'cuda' else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Apply LoRA
            self.model = get_peft_model(self.model, self.lora_config)
            
            # Setup optimizer for LoRA parameters only
            self.optimizer = AdamW(
                [p for p in self.model.parameters() if p.requires_grad],
                lr=self.learning_rate,
                weight_decay=0.01
            )
            
            logger.info("Model initialized successfully with LoRA adapters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            return False
    
    def learn_from_interaction(self, input_text, target_response, context=None):
        """Learn from a single interaction with real weight updates."""
        if not self.model or not self.tokenizer:
            logger.warning("Model not initialized. Call initialize_model() first.")
            return False
        
        with self.learning_lock:
            try:
                # Prepare training data
                conversation = f"{input_text} {target_response}"
                
                # Tokenize
                inputs = self.tokenizer(
                    conversation,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                # Forward pass
                self.model.train()
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                # Update weights
                self.optimizer.step()
                
                # Track learning
                self.total_updates += 1
                self.learning_stats['total_loss'] += loss.item()
                self.learning_stats['avg_loss'] = self.learning_stats['total_loss'] / self.total_updates
                
                learning_record = {
                    'timestamp': time.time(),
                    'input': input_text,
                    'target': target_response,
                    'loss': loss.item(),
                    'update_count': self.total_updates
                }
                self.learning_history.append(learning_record)
                
                logger.info(f"Learning update #{self.total_updates}: loss={loss.item():.4f}")
                return True
                
            except Exception as e:
                logger.error(f"Learning failed: {e}")
                return False
    
    def generate_response(self, input_text, max_length=256, temperature=0.7, do_sample=True):
        """Generate response using the learned model."""
        if not self.model or not self.tokenizer:
            return "Model not initialized. Please call initialize_model() first."
        
        try:
            self.model.eval()
            
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error generating response: {e}"
    
    def save_adapter(self, save_path):
        """Save only the LoRA adapter weights."""
        if not self.model:
            return False
        
        try:
            os.makedirs(save_path, exist_ok=True)
            self.model.save_pretrained(save_path)
            
            # Save learning statistics
            stats_path = os.path.join(save_path, "learning_stats.json")
            with open(stats_path, 'w') as f:
                json.dump(dict(self.learning_stats), f, indent=2)
            
            logger.info(f"LoRA adapter saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save adapter: {e}")
            return False
    
    def load_adapter(self, adapter_path):
        """Load LoRA adapter weights."""
        try:
            if not self.model:
                self.initialize_model()
            
            # Load the adapter
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            
            # Load learning statistics if available
            stats_path = os.path.join(adapter_path, "learning_stats.json")
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    saved_stats = json.load(f)
                    self.learning_stats.update(saved_stats)
            
            logger.info(f"LoRA adapter loaded from {adapter_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load adapter: {e}")
            return False
    
    def get_learning_stats(self):
        """Get current learning statistics."""
        return {
            'total_updates': self.total_updates,
            'average_loss': self.learning_stats.get('avg_loss', 0.0),
            'recent_interactions': len(self.learning_history),
            'model_name': self.model_name,
            'device': str(self.device),
            'lora_rank': self.lora_config.r,
            'learning_rate': self.learning_rate
        }

class ARCTrainer:
    """Main training interface combining all ARC learning components."""
    
    def __init__(self, config=None):
        """Initialize ARC trainer with all components."""
        self.config = config
        
        # Core learning components
        self.transformer = None
        self.memory_system = None
        self.safety_system = None
        
        # Training state
        self.training_history = deque(maxlen=1000)
        self.training_stats = defaultdict(int)
        self.is_initialized = False
    
    def initialize_model(self, model_name="cognitivecomputations/TinyDolphin-2.8-1.1b"):
        """Initialize model with ARC capabilities."""
        try:
            logger.info("Initializing ARC Trainer...")
            
            # Initialize transformer
            self.transformer = LearningARCTransformer(model_name, self.config)
            success = self.transformer.initialize_model()
            
            if not success:
                return False
            
            # BUGFIX: Expose model on trainer for compatibility
            self.model = self.transformer.model
            self.tokenizer = self.transformer.tokenizer
            
            # Initialize memory system
            from .memory import MemorySystem
            self.memory_system = MemorySystem(self.config)
            if hasattr(self.memory_system, 'initialize_consolidation'):
                self.memory_system.initialize_consolidation(self.transformer)
            
            # Initialize safety system
            from .safety import SafetySystem
            self.safety_system = SafetySystem(self.config)
            
            self.is_initialized = True
            logger.info("ARC Trainer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ARC Trainer: {e}")
            return False
    
    def train_on_pack(self, pack_path):
        """Train on a teaching pack."""
        if not self.is_initialized:
            logger.error("Trainer not initialized. Call initialize_model() first.")
            return False
        
        try:
            pack_file = os.path.join(pack_path, "pack.json")
            if not os.path.exists(pack_file):
                logger.error(f"Pack file not found: {pack_file}")
                return False
            
            with open(pack_file, 'r') as f:
                pack_data = json.load(f)
            
            examples = pack_data.get('examples', [])
            if not examples:
                logger.warning("No examples found in pack")
                return False
            
            logger.info(f"Training on pack: {pack_data.get('name', 'Unknown')}")
            
            success_count = 0
            for i, example in enumerate(examples):
                input_text = example.get('input', '')
                target_response = example.get('output', '')
                
                if input_text and target_response:
                    # Learn from this interaction
                    success = self.transformer.learn_from_interaction(
                        input_text, target_response
                    )
                    
                    if success:
                        success_count += 1
                        
                        # Store in memory
                        if self.memory_system:
                            self.memory_system.add_interaction(
                                input_text, target_response, 
                                {'source': 'training_pack', 'pack_name': pack_data.get('name', 'Unknown')}
                            )
                    
                    # Progress logging
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i + 1}/{len(examples)} examples")
            
            self.training_stats['packs_trained'] += 1
            self.training_stats['examples_trained'] += success_count
            
            logger.info(f"Pack training complete: {success_count}/{len(examples)} successful")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to train on pack: {e}")
            return False
    
    def generate_response(self, input_text, **kwargs):
        """Generate response with ARC enhancements."""
        if not self.is_initialized:
            return "Trainer not initialized. Call initialize_model() first."
        
        try:
            # Get relevant memories for context
            relevant_memories = []
            if self.memory_system:
                memories = self.memory_system.get_relevant_memories(input_text, max_results=3)
                relevant_memories = memories
            
            # Generate base response
            response = self.transformer.generate_response(input_text, **kwargs)
            
            # Validate with safety system
            if self.safety_system:
                validation = self.safety_system.validate_response(
                    response, {'user_input': input_text, 'memories': relevant_memories}
                )
                
                if not validation['is_safe']:
                    response = validation['final_response']
                    logger.info(f"Safety system intervention: {validation['issues']}")
            
            # Store interaction in memory
            if self.memory_system:
                self.memory_system.add_interaction(
                    input_text, response, {'source': 'generation'}
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return f"Error generating response: {e}"
    
    def save_model(self, path):
        """Save the trained model and all components."""
        if not self.is_initialized:
            logger.error("Trainer not initialized")
            return False
        
        try:
            os.makedirs(path, exist_ok=True)
            
            # Save transformer adapter
            adapter_path = os.path.join(path, "lora_adapter")
            self.transformer.save_adapter(adapter_path)
            
            # Save training statistics
            stats_path = os.path.join(path, "training_stats.json")
            with open(stats_path, 'w') as f:
                json.dump(dict(self.training_stats), f, indent=2)
            
            # Save memory stats if available
            if self.memory_system:
                memory_stats = self.memory_system.get_memory_stats()
                memory_path = os.path.join(path, "memory_stats.json")
                with open(memory_path, 'w') as f:
                    json.dump(memory_stats, f, indent=2)
            
            # Save safety stats if available
            if self.safety_system:
                safety_stats = self.safety_system.get_safety_stats()
                safety_path = os.path.join(path, "safety_stats.json")
                with open(safety_path, 'w') as f:
                    json.dump(safety_stats, f, indent=2)
            
            logger.info(f"Model saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, path):
        """Load a trained model and all components."""
        try:
            # Load adapter
            adapter_path = os.path.join(path, "lora_adapter")
            if os.path.exists(adapter_path) and self.transformer:
                self.transformer.load_adapter(adapter_path)
            
            # Load training statistics
            stats_path = os.path.join(path, "training_stats.json")
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    saved_stats = json.load(f)
                    self.training_stats.update(saved_stats)
            
            logger.info(f"Model loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def get_training_stats(self):
        """Get comprehensive training statistics."""
        stats = dict(self.training_stats)
        
        if self.transformer:
            stats['transformer'] = self.transformer.get_learning_stats()
        
        if self.memory_system:
            stats['memory'] = self.memory_system.get_memory_stats()
        
        if self.safety_system:
            stats['safety'] = self.safety_system.get_safety_stats()
        
        return stats
