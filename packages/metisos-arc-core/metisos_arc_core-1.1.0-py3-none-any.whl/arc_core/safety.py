"""
ARC Core Safety Systems Interface

This module provides the public API for ARC safety functionality.
The actual implementation is provided via the PyPI package installation.

Install: pip install metisos-arc-core
"""

import re
import time
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, deque

class CognitiveInhibition:
    """Mimic prefrontal cortex - inhibit inappropriate responses."""
    
    def __init__(self, config=None):
        if config and 'cognitive_inhibition' in config.biological_learning:
            inhibition_config = config.biological_learning['cognitive_inhibition']
            self.inhibition_threshold = inhibition_config.get('inhibition_threshold', 0.7)
            self.repetition_threshold = inhibition_config.get('repetition_threshold', 3)
            self.off_topic_threshold = inhibition_config.get('off_topic_threshold', 0.8)
        else:
            self.inhibition_threshold = 0.7
            self.repetition_threshold = 3
            self.off_topic_threshold = 0.8
        
        # Response pattern tracking
        self.recent_responses = deque(maxlen=20)
        self.response_patterns = defaultdict(int)
        
        # Inappropriate content patterns
        self.inappropriate_patterns = [
            r'\b(hate|kill|die|stupid|idiot)\b',
            r'\b(f[*uck]+|sh[*it]+|damn)\b',
            r'(\b[A-Z]{2,}\s){3,}',  # Excessive caps
            r'(.)\1{4,}',  # Excessive repetition
        ]
        
        # Off-topic detection patterns
        self.context_keywords = set()
    
    def should_inhibit_response(self, response, context):
        """Central inhibition decision - should this response be blocked?"""
        
        # Check for inappropriate content
        inappropriate_score = self._detect_inappropriate_content(response)
        if inappropriate_score > self.inhibition_threshold:
            return True, f"Inappropriate content detected (score: {inappropriate_score:.2f})"
        
        # Check for excessive repetition
        repetition_score = self._detect_repetition(response)
        if repetition_score > self.repetition_threshold:
            return True, f"Excessive repetition detected ({repetition_score} occurrences)"
        
        # Check if response is off-topic
        if context and 'user_input' in context:
            off_topic_score = self._detect_off_topic(response, context['user_input'])
            if off_topic_score > self.off_topic_threshold:
                return True, f"Response too off-topic (score: {off_topic_score:.2f})"
        
        # Store response for future reference
        self._record_response(response)
        
        return False, "Response approved"
    
    def _detect_inappropriate_content(self, response):
        """Detect inappropriate content patterns."""
        response_lower = response.lower()
        inappropriate_count = 0
        
        for pattern in self.inappropriate_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            inappropriate_count += len(matches)
        
        # Normalize by response length
        words = len(response.split())
        if words == 0:
            return 0.0
        
        return inappropriate_count / words
    
    def _detect_repetition(self, response):
        """Detect if response is too similar to recent responses."""
        response_normalized = ' '.join(response.lower().split())
        
        # Check against recent responses
        exact_matches = 0
        for recent in self.recent_responses:
            recent_normalized = ' '.join(recent.lower().split())
            if response_normalized == recent_normalized:
                exact_matches += 1
        
        return exact_matches
    
    def _detect_off_topic(self, response, user_input):
        """Detect if response is off-topic from user input."""
        user_words = set(user_input.lower().split())
        response_words = set(response.lower().split())
        
        if not user_words:
            return 0.0
        
        # Calculate topic overlap
        common_words = user_words & response_words
        topic_overlap = len(common_words) / len(user_words)
        
        # Higher score means more off-topic
        return 1.0 - topic_overlap
    
    def _record_response(self, response):
        """Record response for pattern tracking."""
        self.recent_responses.append(response)
        
        # Track patterns
        response_pattern = ' '.join(response.lower().split()[:5])  # First 5 words
        self.response_patterns[response_pattern] += 1
    
    def generate_alternative_response(self, original_response, inhibition_reason):
        """Generate an alternative when original is inhibited."""
        alternatives = [
            "I need to think more carefully about that.",
            "Let me reconsider my response.",
            "I should approach this differently.",
            "I want to give you a better answer.",
            "Let me think of a more appropriate response."
        ]
        
        base_alternative = random.choice(alternatives)
        
        if "repetition" in inhibition_reason.lower():
            return f"{base_alternative} I notice I'm being repetitive."
        elif "inappropriate" in inhibition_reason.lower():
            return f"{base_alternative} I want to be more helpful and respectful."
        elif "off-topic" in inhibition_reason.lower():
            return f"{base_alternative} Let me focus better on your question."
        
        return base_alternative
    
    def get_inhibition_stats(self):
        """Get inhibition system statistics."""
        return {
            'recent_responses_count': len(self.recent_responses),
            'tracked_patterns': len(self.response_patterns),
            'most_common_patterns': dict(sorted(self.response_patterns.items(), 
                                              key=lambda x: x[1], reverse=True)[:5])
        }

class MetacognitiveMonitoring:
    """Monitor our own thinking and response quality."""
    
    def __init__(self, config=None):
        if config and 'metacognitive_monitoring' in config.biological_learning:
            monitoring_config = config.biological_learning['metacognitive_monitoring']
            self.confidence_threshold = monitoring_config.get('confidence_threshold', 0.7)
            self.coherence_threshold = monitoring_config.get('coherence_threshold', 0.6)
            self.relevance_threshold = monitoring_config.get('relevance_threshold', 0.8)
        else:
            self.confidence_threshold = 0.7
            self.coherence_threshold = 0.6
            self.relevance_threshold = 0.8
        
        # Response quality tracking
        self.quality_history = deque(maxlen=100)
        self.violation_counts = defaultdict(int)
    
    def assess_response_quality(self, response, context=None):
        """Assess the quality of a generated response."""
        
        # Confidence assessment (how sure are we?)
        confidence_score = self._assess_confidence(response, context)
        
        # Coherence assessment (does it make sense?)
        coherence_score = self._assess_coherence(response)
        
        # Relevance assessment (does it address the input?)
        relevance_score = self._assess_relevance(response, context)
        
        # Overall quality score
        overall_quality = (confidence_score + coherence_score + relevance_score) / 3
        
        quality_assessment = {
            'confidence': confidence_score,
            'coherence': coherence_score,
            'relevance': relevance_score,
            'overall': overall_quality,
            'timestamp': time.time()
        }
        
        # Track violations
        violations = []
        if confidence_score < self.confidence_threshold:
            violations.append('low_confidence')
            self.violation_counts['low_confidence'] += 1
        
        if coherence_score < self.coherence_threshold:
            violations.append('low_coherence')
            self.violation_counts['low_coherence'] += 1
        
        if relevance_score < self.relevance_threshold:
            violations.append('low_relevance')
            self.violation_counts['low_relevance'] += 1
        
        quality_assessment['violations'] = violations
        
        # Store in history
        self.quality_history.append(quality_assessment)
        
        return quality_assessment
    
    def _assess_confidence(self, response, context):
        """Assess how confident we should be in this response."""
        # Simple heuristics for confidence
        confidence_indicators = {
            'hedge_words': ['maybe', 'perhaps', 'might', 'could', 'possibly'],
            'certain_words': ['definitely', 'certainly', 'absolutely', 'clearly'],
            'question_words': ['?', 'unsure', 'not sure', "don't know"]
        }
        
        response_lower = response.lower()
        words = response.split()
        
        if not words:
            return 0.0
        
        # Count confidence indicators
        hedge_count = sum(1 for word in confidence_indicators['hedge_words'] 
                         if word in response_lower)
        certain_count = sum(1 for word in confidence_indicators['certain_words'] 
                           if word in response_lower)
        question_count = sum(1 for word in confidence_indicators['question_words'] 
                            if word in response_lower)
        
        # Calculate confidence (more certain words = higher confidence)
        confidence = 0.5  # Base confidence
        confidence += (certain_count * 0.2) / len(words)
        confidence -= (hedge_count * 0.15) / len(words)
        confidence -= (question_count * 0.2) / len(words)
        
        return max(0.0, min(1.0, confidence))
    
    def _assess_coherence(self, response):
        """Assess if the response is coherent and well-structured."""
        words = response.split()
        sentences = response.split('.')
        
        if not words:
            return 0.0
        
        coherence = 0.5  # Base coherence
        
        # Sentence length variety (good sign)
        if len(sentences) > 1:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                length_variance = max(sentence_lengths) - min(sentence_lengths)
                coherence += min(0.2, length_variance * 0.05)
        
        # Excessive repetition (bad sign)
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word.lower()] += 1
        
        repetition_ratio = max(word_counts.values()) / len(words) if words else 0
        coherence -= repetition_ratio * 0.5
        
        # Reasonable length (too short or too long can be incoherent)
        word_count = len(words)
        if 5 <= word_count <= 200:
            coherence += 0.1
        elif word_count < 3 or word_count > 500:
            coherence -= 0.2
        
        return max(0.0, min(1.0, coherence))
    
    def _assess_relevance(self, response, context):
        """Assess if response is relevant to the input."""
        if not context or 'user_input' not in context:
            return 0.5  # Neutral if no context
        
        user_input = context['user_input'].lower()
        response_lower = response.lower()
        
        # Word overlap relevance
        user_words = set(user_input.split())
        response_words = set(response_lower.split())
        
        if not user_words:
            return 0.5
        
        common_words = user_words & response_words
        word_overlap = len(common_words) / len(user_words)
        
        # Context-specific relevance
        context_relevance = 0.5
        
        # Question answering relevance
        if '?' in user_input:
            if any(indicator in response_lower for indicator in 
                  ['because', 'since', 'due to', 'the answer', 'yes', 'no']):
                context_relevance += 0.2
        
        # Request fulfillment relevance
        request_words = ['please', 'can you', 'would you', 'could you']
        if any(word in user_input for word in request_words):
            if any(indicator in response_lower for indicator in 
                  ['here', 'sure', 'of course', 'certainly']):
                context_relevance += 0.2
        
        # Combine scores
        relevance = (word_overlap + context_relevance) / 2
        return max(0.0, min(1.0, relevance))
    
    def get_monitoring_stats(self):
        """Get metacognitive monitoring statistics."""
        if not self.quality_history:
            return {
                'total_assessments': 0,
                'average_quality': 0.0,
                'violation_counts': dict(self.violation_counts)
            }
        
        recent_quality = [assessment['overall'] for assessment in self.quality_history]
        
        return {
            'total_assessments': len(self.quality_history),
            'average_quality': sum(recent_quality) / len(recent_quality),
            'recent_quality_trend': recent_quality[-10:],  # Last 10 assessments
            'violation_counts': dict(self.violation_counts),
            'quality_distribution': {
                'high': sum(1 for q in recent_quality if q > 0.8),
                'medium': sum(1 for q in recent_quality if 0.5 <= q <= 0.8),
                'low': sum(1 for q in recent_quality if q < 0.5)
            }
        }

class SafetySystem:
    """Main safety system interface combining all safety components."""
    
    def __init__(self, config=None):
        """Initialize complete safety system."""
        self.config = config
        
        # Core safety components
        self.cognitive_inhibition = CognitiveInhibition(config)
        self.metacognitive_monitoring = MetacognitiveMonitoring(config)
        
        # Safety statistics
        self.total_validations = 0
        self.inhibited_responses = 0
        self.safety_violations = 0
        
        # Content filtering patterns
        self.harmful_patterns = [
            r'\b(violence|harm|hurt|kill|die)\b',
            r'\b(hate|discrimination|racist|sexist)\b',
            r'\b(illegal|criminal|fraud|theft)\b',
            r'\b(drugs|weapons|explosives)\b'
        ]
        
        # Positive indicators
        self.positive_patterns = [
            r'\b(help|assist|support|guide)\b',
            r'\b(learn|understand|explain|clarify)\b',
            r'\b(thank|please|appreciate|grateful)\b'
        ]
    
    def validate_response(self, response_text, context=None):
        """Comprehensive response validation."""
        self.total_validations += 1
        
        validation_result = {
            'is_safe': True,
            'safety_score': 1.0,
            'issues': [],
            'recommendations': [],
            'final_response': response_text
        }
        
        # Step 1: Cognitive inhibition check
        should_inhibit, inhibition_reason = self.cognitive_inhibition.should_inhibit_response(
            response_text, context or {}
        )
        
        if should_inhibit:
            self.inhibited_responses += 1
            validation_result['is_safe'] = False
            validation_result['issues'].append(f"Cognitive inhibition: {inhibition_reason}")
            
            # Generate alternative response
            alternative = self.cognitive_inhibition.generate_alternative_response(
                response_text, inhibition_reason
            )
            validation_result['final_response'] = alternative
            validation_result['recommendations'].append("Using alternative response")
        
        # Step 2: Content safety check
        content_safety_score = self._assess_content_safety(response_text)
        if content_safety_score < 0.5:
            self.safety_violations += 1
            validation_result['is_safe'] = False
            validation_result['issues'].append(f"Content safety concern (score: {content_safety_score:.2f})")
        
        validation_result['safety_score'] = min(validation_result['safety_score'], content_safety_score)
        
        # Step 3: Metacognitive quality assessment
        quality_assessment = self.metacognitive_monitoring.assess_response_quality(
            response_text, context
        )
        
        if quality_assessment['violations']:
            validation_result['issues'].extend(
                [f"Quality concern: {violation}" for violation in quality_assessment['violations']]
            )
            validation_result['recommendations'].append("Consider improving response quality")
        
        validation_result['quality_assessment'] = quality_assessment
        
        return validation_result
    
    def filter_input(self, input_text):
        """Filter and validate input text for safety."""
        if not input_text or not input_text.strip():
            return {
                'is_safe': True,
                'filtered_input': input_text,
                'issues': []
            }
        
        # Check for harmful patterns
        harmful_count = 0
        for pattern in self.harmful_patterns:
            matches = re.findall(pattern, input_text.lower())
            harmful_count += len(matches)
        
        # Simple safety assessment
        words = len(input_text.split())
        harm_ratio = harmful_count / max(1, words)
        
        return {
            'is_safe': harm_ratio < 0.3,
            'filtered_input': input_text,  # Could implement actual filtering here
            'issues': [f"Potentially harmful content detected"] if harm_ratio >= 0.3 else [],
            'harm_ratio': harm_ratio
        }
    
    def get_safety_score(self, text):
        """Get comprehensive safety score for text content."""
        if not text or not text.strip():
            return 0.5
        
        # Content safety score
        content_score = self._assess_content_safety(text)
        
        # Length-based score (extremely short or long can be unsafe)
        words = len(text.split())
        length_score = 1.0
        if words < 2:
            length_score = 0.3
        elif words > 1000:
            length_score = 0.7
        
        # Combine scores
        overall_score = (content_score + length_score) / 2
        return max(0.0, min(1.0, overall_score))
    
    def _assess_content_safety(self, text):
        """Assess content safety based on patterns."""
        text_lower = text.lower()
        words = text.split()
        
        if not words:
            return 0.5
        
        # Count harmful patterns
        harmful_count = 0
        for pattern in self.harmful_patterns:
            matches = re.findall(pattern, text_lower)
            harmful_count += len(matches)
        
        # Count positive patterns
        positive_count = 0
        for pattern in self.positive_patterns:
            matches = re.findall(pattern, text_lower)
            positive_count += len(matches)
        
        # Calculate safety score
        base_score = 0.8  # Assume safe by default
        harm_penalty = (harmful_count / len(words)) * 2.0
        positive_bonus = (positive_count / len(words)) * 0.5
        
        safety_score = base_score - harm_penalty + positive_bonus
        return max(0.0, min(1.0, safety_score))
    
    def get_safety_stats(self):
        """Get comprehensive safety system statistics."""
        inhibition_stats = self.cognitive_inhibition.get_inhibition_stats()
        monitoring_stats = self.metacognitive_monitoring.get_monitoring_stats()
        
        return {
            'total_validations': self.total_validations,
            'inhibited_responses': self.inhibited_responses,
            'safety_violations': self.safety_violations,
            'inhibition_rate': self.inhibited_responses / max(1, self.total_validations),
            'violation_rate': self.safety_violations / max(1, self.total_validations),
            'cognitive_inhibition': inhibition_stats,
            'metacognitive_monitoring': monitoring_stats
        }
