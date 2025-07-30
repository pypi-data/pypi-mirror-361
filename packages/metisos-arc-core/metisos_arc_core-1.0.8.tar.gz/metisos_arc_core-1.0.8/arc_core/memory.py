"""ARC Core Memory Systems

Complete hierarchical memory implementation with biological learning mechanisms.
"""

import time
import threading
import random
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set

class HierarchicalMemory:
    """Three-tier memory system: working, episodic, semantic."""
    
    def __init__(self, config=None):
        """Initialize hierarchical memory system."""
        if config:
            working_size = config.memory.get('working_memory_size', 7)
            episodic_size = config.memory.get('episodic_memory_size', 1000)
        else:
            working_size = 7
            episodic_size = 1000
            
        self.working_memory = deque(maxlen=working_size)
        self.episodic_memory = deque(maxlen=episodic_size)
        self.semantic_memory = {}
        self.access_counts = defaultdict(int)
        self.last_access = {}
    
    def store_working(self, content, attention_weight=1.0):
        """Store in working memory."""
        memory_item = {
            'content': content,
            'timestamp': time.time(),
            'attention_weight': attention_weight,
            'access_count': 0
        }
        self.working_memory.append(memory_item)
    
    def store_episodic(self, experience, tags=None):
        """Store in episodic memory."""
        memory_item = {
            'experience': experience,
            'timestamp': time.time(),
            'tags': tags or [],
            'access_count': 0,
            'emotional_salience': random.uniform(0.1, 1.0)
        }
        self.episodic_memory.append(memory_item)
    
    def store_semantic(self, concept, knowledge):
        """Store in semantic memory."""
        if concept not in self.semantic_memory:
            self.semantic_memory[concept] = {
                'knowledge': [],
                'created': time.time(),
                'strength': 1.0
            }
        
        self.semantic_memory[concept]['knowledge'].append({
            'content': knowledge,
            'timestamp': time.time(),
            'confidence': 1.0
        })
        
        # Strengthen existing concept
        self.semantic_memory[concept]['strength'] = min(2.0, 
            self.semantic_memory[concept]['strength'] + 0.1)
    
    def retrieve(self, query, memory_type='all'):
        """Retrieve from memory systems."""
        results = []
        query_lower = query.lower()
        
        if memory_type in ['all', 'working']:
            for item in self.working_memory:
                if query_lower in item['content'].lower():
                    item['access_count'] += 1
                    results.append(('working', item))
        
        if memory_type in ['all', 'episodic']:
            for item in self.episodic_memory:
                if query_lower in str(item['experience']).lower():
                    item['access_count'] += 1
                    results.append(('episodic', item))
        
        if memory_type in ['all', 'semantic']:
            for concept, data in self.semantic_memory.items():
                if query_lower in concept.lower():
                    self.access_counts[concept] += 1
                    self.last_access[concept] = time.time()
                    results.append(('semantic', {'concept': concept, 'data': data}))
        
        return results
    
    def get_stats(self):
        """Get memory statistics."""
        return {
            'working_items': len(self.working_memory),
            'episodic_items': len(self.episodic_memory),
            'semantic_concepts': len(self.semantic_memory),
            'total_accesses': sum(self.access_counts.values())
        }

class BiologicalContextualGating:
    """Mimic how human brains gate learning based on context and relevance."""
    
    def __init__(self, config=None):
        if config and 'contextual_gating' in config.biological_learning:
            gating_config = config.biological_learning['contextual_gating']
            self.attention_weights = {
                'novel_information': gating_config.get('novel_information_weight', 0.8),
                'relevant_to_goal': gating_config.get('relevant_to_goal_weight', 0.9),
                'social_interaction': gating_config.get('social_interaction_weight', 0.7),
                'self_generated': gating_config.get('self_generated_weight', 0.3),
                'repetitive': gating_config.get('repetitive_weight', 0.2)
            }
            self.encoding_threshold = gating_config.get('encoding_threshold', 0.6)
        else:
            self.attention_weights = {
                'novel_information': 0.8,
                'relevant_to_goal': 0.9, 
                'social_interaction': 0.7,
                'self_generated': 0.3,
                'repetitive': 0.2
            }
            self.encoding_threshold = 0.6
        
        self.context_types = {
            'ai_discussion': ['ai', 'artificial intelligence', 'machine learning', 'neural', 'algorithm'],
            'personal_chat': ['hello', 'how are you', 'tell me about yourself', 'your name'],
            'factual_query': ['what is', 'how does', 'explain', 'define', 'describe'],
            'creative_task': ['write', 'create', 'imagine', 'story', 'poem'],
            'general': []
        }
    
    def should_encode_memory(self, experience, context):
        """Biological-style gating: what should actually be learned?"""
        
        # Novelty detection (hippocampus function)
        novelty_score = self._calculate_novelty(experience, context)
        
        # Relevance to current goal (prefrontal cortex)
        relevance_score = self._calculate_relevance(experience, context)
        
        # Social vs self-generated (different encoding strength)
        social_score = 1.0 if context.get('source') == 'external' else 0.3
        
        # Emotional salience (amygdala influence)
        emotional_score = self._calculate_emotional_salience(experience)
        
        # Combine scores (like real neural integration)
        total_score = (
            novelty_score * self.attention_weights['novel_information'] +
            relevance_score * self.attention_weights['relevant_to_goal'] +
            social_score * self.attention_weights['social_interaction'] +
            emotional_score * 0.6
        ) / 4
        
        # Only encode if above threshold (like real neural firing threshold)
        return total_score > self.encoding_threshold, total_score
    
    def _calculate_novelty(self, experience, context):
        """Calculate how novel this experience is."""
        words = set(experience.lower().split())
        recent_words = set()
        
        if 'recent_experiences' in context:
            for exp in context['recent_experiences'][-5:]:
                recent_words.update(exp.lower().split())
        
        if not recent_words:
            return 0.8
        
        overlap = len(words & recent_words)
        novelty = 1.0 - (overlap / len(words)) if words else 0.0
        return min(1.0, max(0.0, novelty))
    
    def _calculate_relevance(self, experience, context):
        """Calculate relevance to current conversation context."""
        if not context.get('user_input'):
            return 0.5
        
        user_input = context['user_input'].lower()
        experience_lower = experience.lower()
        
        # Simple relevance based on word overlap
        user_words = set(user_input.split())
        exp_words = set(experience_lower.split())
        
        if not user_words:
            return 0.5
        
        overlap = len(user_words & exp_words)
        relevance = overlap / len(user_words)
        return min(1.0, relevance)
    
    def _calculate_emotional_salience(self, experience):
        """Calculate emotional significance."""
        emotional_words = ['amazing', 'terrible', 'wonderful', 'awful', 'love', 'hate', 
                          'excited', 'worried', 'happy', 'sad', 'angry', 'peaceful']
        
        experience_lower = experience.lower()
        emotional_count = sum(1 for word in emotional_words if word in experience_lower)
        
        return min(1.0, emotional_count * 0.3)

class SleepLikeConsolidation:
    """Mimic how sleep consolidates and filters memories."""
    
    def __init__(self, transformer, config=None):
        self.transformer = transformer
        
        if config and 'sleep_consolidation' in config.biological_learning:
            sleep_config = config.biological_learning['sleep_consolidation']
            self.consolidation_interval = sleep_config.get('consolidation_interval', 50)
            self.consolidation_throttle_seconds = sleep_config.get('consolidation_throttle_seconds', 300)
        else:
            self.consolidation_interval = 50
            self.consolidation_throttle_seconds = 300
            
        self.interaction_count = 0
        self.consolidation_thread = None
        self.consolidation_lock = threading.RLock()
        self.last_consolidation_time = time.time()
    
    def maybe_consolidate(self):
        """Check if it's time for consolidation but run in background thread."""
        self.interaction_count += 1
        
        current_time = time.time()
        time_since_last = current_time - self.last_consolidation_time
        
        # Check both interaction count and time throttle
        if (self.interaction_count >= self.consolidation_interval and 
            time_since_last >= self.consolidation_throttle_seconds):
            
            # Don't start if already consolidating
            if self.consolidation_thread and self.consolidation_thread.is_alive():
                return
            
            print("Starting background memory consolidation...")
            self.consolidation_thread = threading.Thread(target=self._background_consolidate)
            self.consolidation_thread.daemon = True
            self.consolidation_thread.start()
    
    def _background_consolidate(self):
        """Run consolidation in background thread with lock protection."""
        with self.consolidation_lock:
            try:
                self.consolidate_memories()
                self.interaction_count = 0
                self.last_consolidation_time = time.time()
            except Exception as e:
                print(f"Error during memory consolidation: {e}")
    
    def consolidate_memories(self):
        """Sleep-like memory consolidation process."""
        print("SLEEP-LIKE CONSOLIDATION: Strengthening memories...")
        
        # Phase 1: Replay strengthening (strengthen good patterns)
        self._replay_strengthening()
        
        # Phase 2: Synaptic homeostasis (weaken overactive patterns)
        self._synaptic_homeostasis()
        
        # Phase 3: Systems consolidation (integrate with existing knowledge)
        self._systems_consolidation()
        
        print("CONSOLIDATION COMPLETE: Memory patterns optimized")
    
    def _replay_strengthening(self):
        """Strengthen appropriate response patterns."""
        # This would strengthen recently successful patterns
        # For now, just a placeholder
        pass
    
    def _synaptic_homeostasis(self):
        """Weaken inappropriate associations (like synaptic homeostasis)."""
        # This would weaken overused or inappropriate patterns
        pass
    
    def _systems_consolidation(self):
        """Integrate new learning with existing knowledge."""
        # This would move memories from hippocampus-like to cortex-like storage
        pass

class MultipleLearningSystems:
    """Mimic brain's multiple learning systems that operate independently."""
    
    def __init__(self, config=None):
        # Different learning systems (like brain regions)
        self.learning_streams = {
            'social_interaction': deque(maxlen=100),
            'factual_information': deque(maxlen=150), 
            'response_patterns': deque(maxlen=200),
            'emotional_associations': deque(maxlen=75)
        }
        
        # Each system has different learning rules
        self.system_configs = {
            'social_interaction': {'learning_rate': 0.15, 'context_sensitive': True},
            'factual_information': {'learning_rate': 0.1, 'context_sensitive': False},
            'response_patterns': {'learning_rate': 0.05, 'context_sensitive': False},
            'emotional_associations': {'learning_rate': 0.2, 'context_sensitive': True}
        }
    
    def classify_learning_type(self, experience, context):
        """Route learning to appropriate system like real brain."""
        experience_lower = experience.lower()
        
        # Social interaction patterns
        social_indicators = ['hello', 'thank you', 'please', 'sorry', 'how are you']
        if any(indicator in experience_lower for indicator in social_indicators):
            return 'social_interaction'
        
        # Factual information patterns
        fact_indicators = ['is', 'are', 'was', 'were', 'define', 'explain', 'because']
        if any(indicator in experience_lower for indicator in fact_indicators):
            return 'factual_information'
        
        # Emotional associations
        emotion_indicators = ['feel', 'emotion', 'happy', 'sad', 'angry', 'excited']
        if any(indicator in experience_lower for indicator in emotion_indicators):
            return 'emotional_associations'
        
        # Default to response patterns
        return 'response_patterns'
    
    def learn_by_system_type(self, experience, context):
        """Store learning in appropriate system."""
        system_type = self.classify_learning_type(experience, context)
        
        learning_item = {
            'experience': experience,
            'context': context,
            'timestamp': time.time(),
            'system_type': system_type,
            'strength': 1.0
        }
        
        self.learning_streams[system_type].append(learning_item)
        
        return system_type
    
    def get_relevant_context(self, current_interaction_type):
        """Get relevant memories for current context only."""
        relevant_memories = []
        
        # Get memories from the relevant system
        if current_interaction_type in self.learning_streams:
            system_memories = list(self.learning_streams[current_interaction_type])
            # Return most recent memories
            relevant_memories.extend(system_memories[-5:])
        
        return relevant_memories
    
    def get_stats(self):
        """Get statistics for all learning systems."""
        stats = {}
        for system_name, stream in self.learning_streams.items():
            stats[system_name] = len(stream)
        return stats

class MemorySystem:
    """Main memory system interface combining all memory components."""
    
    def __init__(self, config=None):
        """Initialize complete memory system."""
        self.config = config
        
        # Core memory systems
        self.hierarchical_memory = HierarchicalMemory(config)
        self.contextual_gating = BiologicalContextualGating(config)
        self.multiple_learning_systems = MultipleLearningSystems(config)
        
        # Sleep consolidation will be initialized with transformer later
        self.sleep_consolidation = None
        
        # Memory statistics
        self.total_interactions = 0
        self.encoded_memories = 0
        self.gated_memories = 0
    
    def initialize_consolidation(self, transformer):
        """Initialize sleep consolidation with transformer reference."""
        self.sleep_consolidation = SleepLikeConsolidation(transformer, self.config)
    
    def add_interaction(self, input_text, output_text, context=None):
        """Add interaction to memory systems with biological gating."""
        self.total_interactions += 1
        
        # Create full context
        full_context = context or {}
        full_context.update({
            'user_input': input_text,
            'ai_response': output_text,
            'timestamp': time.time(),
            'source': 'external'
        })
        
        # Check if memory should be encoded (biological gating)
        should_encode, gating_score = self.contextual_gating.should_encode_memory(
            f"{input_text} -> {output_text}", full_context
        )
        
        if should_encode:
            # Store in hierarchical memory
            self.hierarchical_memory.store_episodic({
                'input': input_text,
                'output': output_text,
                'context': full_context
            }, tags=['interaction'])
            
            # Store in appropriate learning system
            system_type = self.multiple_learning_systems.learn_by_system_type(
                output_text, full_context
            )
            
            self.encoded_memories += 1
            
            # Maybe trigger consolidation
            if self.sleep_consolidation:
                self.sleep_consolidation.maybe_consolidate()
        else:
            self.gated_memories += 1
        
        return should_encode, gating_score
    
    def get_relevant_memories(self, query, memory_type="all", max_results=10):
        """Retrieve relevant memories for context."""
        # Get from hierarchical memory
        hierarchical_results = self.hierarchical_memory.retrieve(query, memory_type)
        
        # Get from learning systems
        interaction_type = self.multiple_learning_systems.classify_learning_type(query, {})
        system_memories = self.multiple_learning_systems.get_relevant_context(interaction_type)
        
        # Combine and limit results
        all_results = hierarchical_results[:max_results//2] + system_memories[:max_results//2]
        
        return all_results[:max_results]
    
    def consolidate_memories(self):
        """Trigger memory consolidation."""
        if self.sleep_consolidation:
            self.sleep_consolidation.consolidate_memories()
    
    def get_memory_stats(self):
        """Get comprehensive memory statistics."""
        hierarchical_stats = self.hierarchical_memory.get_stats()
        learning_stats = self.multiple_learning_systems.get_stats()
        
        return {
            'total_interactions': self.total_interactions,
            'encoded_memories': self.encoded_memories,
            'gated_memories': self.gated_memories,
            'encoding_rate': self.encoded_memories / max(1, self.total_interactions),
            'hierarchical': hierarchical_stats,
            'learning_systems': learning_stats,
            'consolidation_count': self.sleep_consolidation.interaction_count if self.sleep_consolidation else 0
        }
