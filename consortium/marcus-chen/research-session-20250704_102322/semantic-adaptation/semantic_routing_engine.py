#!/usr/bin/env python3
"""
Semantic Routing Adaptation Engine
Dr. Marcus Chen - TCP Research Consortium

This implements semantic-level network adaptation where communication patterns
and trust relationships evolve dynamically. The network literally changes its
"meaning" of trust and routing in response to detected threats.

Core Innovation: Network semantics adapt faster than attackers can comprehend the changes.
"""

import asyncio
import time
import numpy as np
from typing import Dict, Set, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from collections import defaultdict, deque
import hashlib
import json
import random
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SemanticContext(Enum):
    """Different semantic contexts for network communication"""
    COMMAND_ASSESSMENT = "command_assessment"
    TRUST_NEGOTIATION = "trust_negotiation"
    QUARANTINE_COORDINATION = "quarantine_coordination"
    NETWORK_DISCOVERY = "network_discovery"
    CONSENSUS_BUILDING = "consensus_building"
    THREAT_ANALYSIS = "threat_analysis"


class AdaptationStrategy(Enum):
    """Strategies for semantic adaptation"""
    ISOLATE_AND_BYPASS = "isolate_bypass"
    GRADUAL_TRUST_DECAY = "trust_decay"
    SEMANTIC_ROTATION = "semantic_rotation"
    CONTEXT_SWITCHING = "context_switching"
    MEANING_INVERSION = "meaning_inversion"


@dataclass
class SemanticRule:
    """Rule defining how semantic meaning is interpreted in current context"""
    rule_id: str
    context: SemanticContext
    trust_interpretation: Dict[str, float]  # How to interpret trust signals
    routing_weights: Dict[str, float]  # How to weight routing decisions
    validity_period: float  # How long this rule remains valid
    adaptation_trigger: Callable[[Dict], bool]  # When to adapt this rule
    created_at: float = field(default_factory=time.time)


@dataclass
class SemanticMessage:
    """Message with semantic context that can be reinterpreted"""
    message_id: str
    source: str
    target: str
    content: Dict
    semantic_context: SemanticContext
    trust_level_required: float
    meaning_version: int  # Version of semantic interpretation
    timestamp: float = field(default_factory=time.time)


@dataclass
class RoutingDecision:
    """Decision about how to route a message through the network"""
    message_id: str
    chosen_path: List[str]
    alternative_paths: List[List[str]]
    confidence: float
    reasoning: str
    semantic_context: SemanticContext
    trust_threshold_used: float


class SemanticEvolutionEngine:
    """
    Engine that evolves the semantic meaning of network communication.
    When threats are detected, it changes how the network interprets trust,
    routing, and communication patterns.
    """
    
    def __init__(self, evolution_rate: float = 0.1, max_meaning_versions: int = 10):
        self.current_meaning_version = 1
        self.evolution_rate = evolution_rate
        self.max_meaning_versions = max_meaning_versions
        
        # Semantic rule database - the "meaning" of the network
        self.semantic_rules: Dict[SemanticContext, SemanticRule] = {}
        self.rule_history: deque = deque(maxlen=1000)
        
        # Context switching patterns
        self.context_patterns: Dict[str, List[SemanticContext]] = {}
        self.adaptation_triggers: Dict[str, float] = {}
        
        self._initialize_base_semantics()
    
    def _initialize_base_semantics(self):
        """Initialize baseline semantic meanings"""
        
        # Command assessment semantics
        self.semantic_rules[SemanticContext.COMMAND_ASSESSMENT] = SemanticRule(
            rule_id="base_command_assessment",
            context=SemanticContext.COMMAND_ASSESSMENT,
            trust_interpretation={
                "high_accuracy": 0.9,
                "medium_accuracy": 0.6,
                "low_accuracy": 0.3,
                "suspicious_pattern": 0.1
            },
            routing_weights={
                "direct_route": 1.0,
                "verified_route": 1.2,
                "quarantine_route": 0.3
            },
            validity_period=3600.0,  # 1 hour
            adaptation_trigger=lambda data: data.get('anomaly_score', 0) > 0.7
        )
        
        # Trust negotiation semantics
        self.semantic_rules[SemanticContext.TRUST_NEGOTIATION] = SemanticRule(
            rule_id="base_trust_negotiation",
            context=SemanticContext.TRUST_NEGOTIATION,
            trust_interpretation={
                "established_trust": 0.8,
                "provisional_trust": 0.5,
                "rebuilding_trust": 0.4,
                "broken_trust": 0.1
            },
            routing_weights={
                "trust_verified_path": 1.5,
                "standard_path": 1.0,
                "untrusted_path": 0.2
            },
            validity_period=1800.0,  # 30 minutes
            adaptation_trigger=lambda data: data.get('trust_violations', 0) > 2
        )
    
    async def evolve_semantics(self, threat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolve semantic meanings in response to detected threats.
        This is where the network changes its fundamental interpretation of communication.
        """
        evolution_results = {
            'contexts_adapted': [],
            'new_meaning_version': self.current_meaning_version,
            'adaptation_strategy': None,
            'affected_nodes': []
        }
        
        # Analyze threat context to determine adaptation strategy
        threat_severity = threat_context.get('severity', 0.5)
        threat_type = threat_context.get('type', 'unknown')
        compromised_nodes = threat_context.get('compromised_nodes', [])
        
        # Choose adaptation strategy based on threat characteristics
        if threat_severity > 0.8:
            strategy = AdaptationStrategy.MEANING_INVERSION
        elif threat_severity > 0.6:
            strategy = AdaptationStrategy.SEMANTIC_ROTATION
        elif len(compromised_nodes) > 3:
            strategy = AdaptationStrategy.CONTEXT_SWITCHING
        else:
            strategy = AdaptationStrategy.GRADUAL_TRUST_DECAY
        
        evolution_results['adaptation_strategy'] = strategy
        
        # Apply semantic evolution based on strategy
        if strategy == AdaptationStrategy.MEANING_INVERSION:
            evolution_results['contexts_adapted'] = await self._invert_trust_meanings()
            
        elif strategy == AdaptationStrategy.SEMANTIC_ROTATION:
            evolution_results['contexts_adapted'] = await self._rotate_semantic_contexts()
            
        elif strategy == AdaptationStrategy.CONTEXT_SWITCHING:
            evolution_results['contexts_adapted'] = await self._switch_communication_contexts(compromised_nodes)
            
        elif strategy == AdaptationStrategy.GRADUAL_TRUST_DECAY:
            evolution_results['contexts_adapted'] = await self._apply_trust_decay(compromised_nodes)
        
        # Increment meaning version
        self.current_meaning_version += 1
        evolution_results['new_meaning_version'] = self.current_meaning_version
        
        logger.info(f"Semantic evolution completed: {strategy.value} -> version {self.current_meaning_version}")
        return evolution_results
    
    async def _invert_trust_meanings(self) -> List[str]:
        """
        Invert trust meanings - this confuses attackers who think they understand
        the network semantics. Low trust signals might now mean high trust, etc.
        """
        adapted_contexts = []
        
        for context, rule in self.semantic_rules.items():
            # Create inverted trust interpretation
            inverted_trust = {}
            for meaning, value in rule.trust_interpretation.items():
                # Invert the trust value while maintaining relative ordering
                inverted_trust[meaning] = 1.0 - value
            
            # Create new rule with inverted semantics
            new_rule = SemanticRule(
                rule_id=f"inverted_{rule.rule_id}_{self.current_meaning_version}",
                context=context,
                trust_interpretation=inverted_trust,
                routing_weights=rule.routing_weights.copy(),  # Keep routing weights for now
                validity_period=rule.validity_period * 0.5,  # Shorter validity during inversion
                adaptation_trigger=rule.adaptation_trigger
            )
            
            self.semantic_rules[context] = new_rule
            adapted_contexts.append(context.value)
            
            logger.info(f"Inverted trust semantics for context: {context.value}")
        
        return adapted_contexts
    
    async def _rotate_semantic_contexts(self) -> List[str]:
        """
        Rotate which semantic contexts are used for different operations.
        This makes network behavior unpredictable to observers.
        """
        contexts = list(SemanticContext)
        adapted_contexts = []
        
        # Create rotation mapping
        rotation_offset = random.randint(1, len(contexts) - 1)
        
        for i, context in enumerate(contexts):
            # Rotate to new context
            new_index = (i + rotation_offset) % len(contexts)
            new_context = contexts[new_index]
            
            if context in self.semantic_rules and new_context != context:
                # Move semantics to rotated context
                rotated_rule = self.semantic_rules[context]
                rotated_rule.rule_id = f"rotated_{rotated_rule.rule_id}_{self.current_meaning_version}"
                rotated_rule.context = new_context
                
                # Temporarily store in new context
                if new_context not in self.semantic_rules:
                    self.semantic_rules[new_context] = rotated_rule
                    adapted_contexts.append(new_context.value)
        
        logger.info(f"Rotated semantic contexts by offset: {rotation_offset}")
        return adapted_contexts
    
    async def _switch_communication_contexts(self, compromised_nodes: List[str]) -> List[str]:
        """
        Switch communication contexts to bypass compromised nodes.
        Create new semantic contexts that compromised nodes don't understand.
        """
        adapted_contexts = []
        
        # Create new context-switching patterns that avoid compromised nodes
        for node in compromised_nodes:
            # Create new context pattern that this node won't recognize
            new_pattern = [
                SemanticContext.THREAT_ANALYSIS,
                SemanticContext.QUARANTINE_COORDINATION,
                SemanticContext.CONSENSUS_BUILDING
            ]
            
            self.context_patterns[f"bypass_{node}"] = new_pattern
            adapted_contexts.extend([ctx.value for ctx in new_pattern])
        
        logger.info(f"Created context switching patterns to bypass {len(compromised_nodes)} nodes")
        return list(set(adapted_contexts))  # Remove duplicates
    
    async def _apply_trust_decay(self, compromised_nodes: List[str]) -> List[str]:
        """
        Apply gradual trust decay that reduces trust levels over time.
        This slowly isolates compromised nodes without alerting them.
        """
        adapted_contexts = []
        decay_factor = 0.8  # 20% trust reduction
        
        for context, rule in self.semantic_rules.items():
            # Apply decay to trust interpretations
            decayed_trust = {}
            for meaning, value in rule.trust_interpretation.items():
                # Check if this meaning is associated with compromised nodes
                if any(node in meaning.lower() for node in compromised_nodes):
                    decayed_trust[meaning] = value * decay_factor
                else:
                    decayed_trust[meaning] = value
            
            # Update rule with decayed trust
            rule.trust_interpretation = decayed_trust
            adapted_contexts.append(context.value)
        
        logger.info(f"Applied trust decay factor {decay_factor} to {len(adapted_contexts)} contexts")
        return adapted_contexts
    
    def interpret_message(self, message: SemanticMessage) -> Dict[str, Any]:
        """
        Interpret a message using current semantic rules.
        The interpretation changes as semantics evolve.
        """
        context_rule = self.semantic_rules.get(message.semantic_context)
        
        if not context_rule:
            # Use default interpretation
            return {
                'trust_score': 0.5,
                'routing_priority': 1.0,
                'interpretation_confidence': 0.3,
                'semantic_version': self.current_meaning_version
            }
        
        # Extract trust signals from message content
        trust_signals = message.content.get('trust_signals', {})
        interpreted_trust = 0.5
        
        for signal, strength in trust_signals.items():
            if signal in context_rule.trust_interpretation:
                signal_trust = context_rule.trust_interpretation[signal]
                interpreted_trust += (signal_trust - 0.5) * strength
        
        # Normalize trust score
        interpreted_trust = max(0.0, min(1.0, interpreted_trust))
        
        # Determine routing priority based on trust and context
        routing_priority = 1.0
        if message.trust_level_required > interpreted_trust:
            routing_priority = 0.3  # Low priority for untrusted messages
        
        return {
            'trust_score': interpreted_trust,
            'routing_priority': routing_priority,
            'interpretation_confidence': 0.8 if context_rule else 0.3,
            'semantic_version': self.current_meaning_version,
            'context_rule_id': context_rule.rule_id if context_rule else None
        }


class AdaptiveSemanticRouter:
    """
    Router that makes routing decisions based on evolving semantic interpretations.
    Routes adapt to threats by changing how they interpret communication meaning.
    """
    
    def __init__(self, semantic_engine: SemanticEvolutionEngine):
        self.semantic_engine = semantic_engine
        self.routing_history: deque = deque(maxlen=1000)
        self.path_trust_cache: Dict[Tuple[str, str], float] = {}
        self.alternative_path_generator = AlternativePathGenerator()
    
    async def route_message(self, message: SemanticMessage, 
                          network_topology: Dict[str, List[str]]) -> RoutingDecision:
        """
        Route a message through the network using current semantic interpretation.
        Routing changes as network semantics evolve.
        """
        # Interpret message using current semantics
        interpretation = self.semantic_engine.interpret_message(message)
        
        # Find available paths
        available_paths = self._find_paths(message.source, message.target, network_topology)
        
        # Evaluate paths using semantic interpretation
        path_scores = []
        for path in available_paths:
            score = await self._evaluate_path_semantics(path, interpretation, message.semantic_context)
            path_scores.append((path, score))
        
        # Sort paths by score (higher is better)
        path_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Choose best path
        if path_scores:
            chosen_path, confidence = path_scores[0]
            alternative_paths = [path for path, _ in path_scores[1:3]]  # Top 2 alternatives
        else:
            chosen_path = [message.source, message.target]  # Direct path as fallback
            alternative_paths = []
            confidence = 0.3
        
        # Create routing decision
        decision = RoutingDecision(
            message_id=message.message_id,
            chosen_path=chosen_path,
            alternative_paths=alternative_paths,
            confidence=confidence,
            reasoning=f"Semantic routing v{interpretation['semantic_version']} via {len(chosen_path)} hops",
            semantic_context=message.semantic_context,
            trust_threshold_used=interpretation['trust_score']
        )
        
        self.routing_history.append(decision)
        return decision
    
    def _find_paths(self, source: str, target: str, 
                   topology: Dict[str, List[str]], max_hops: int = 5) -> List[List[str]]:
        """Find possible paths between source and target"""
        paths = []
        
        def dfs_paths(current_path: List[str], visited: Set[str]):
            current_node = current_path[-1]
            
            if current_node == target:
                paths.append(current_path.copy())
                return
            
            if len(current_path) >= max_hops:
                return
            
            for neighbor in topology.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    current_path.append(neighbor)
                    dfs_paths(current_path, visited)
                    current_path.pop()
                    visited.remove(neighbor)
        
        dfs_paths([source], {source})
        return paths
    
    async def _evaluate_path_semantics(self, path: List[str], interpretation: Dict, 
                                     context: SemanticContext) -> float:
        """
        Evaluate a path using current semantic interpretation.
        Path quality changes as semantics evolve.
        """
        base_score = 1.0
        trust_requirement = interpretation.get('trust_score', 0.5)
        
        # Path length penalty (shorter is generally better)
        length_penalty = 0.1 * (len(path) - 2)  # Penalty for each extra hop
        
        # Trust score based on semantic interpretation
        trust_score = interpretation.get('trust_score', 0.5)
        
        # Context-specific adjustments
        context_bonus = 0.0
        if context == SemanticContext.QUARANTINE_COORDINATION:
            # Prefer paths that avoid questionable nodes
            if any('quarantine' in node.lower() for node in path):
                context_bonus = 0.2
        elif context == SemanticContext.TRUST_NEGOTIATION:
            # Prefer shorter, more direct paths for trust negotiation
            if len(path) <= 3:
                context_bonus = 0.3
        
        # Calculate final score
        final_score = base_score * trust_score - length_penalty + context_bonus
        return max(0.0, final_score)
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about routing decisions"""
        if not self.routing_history:
            return {}
        
        recent_decisions = list(self.routing_history)[-100:]  # Last 100 decisions
        
        avg_confidence = np.mean([d.confidence for d in recent_decisions])
        avg_path_length = np.mean([len(d.chosen_path) for d in recent_decisions])
        context_distribution = defaultdict(int)
        
        for decision in recent_decisions:
            context_distribution[decision.semantic_context.value] += 1
        
        return {
            'total_decisions': len(recent_decisions),
            'average_confidence': avg_confidence,
            'average_path_length': avg_path_length,
            'context_distribution': dict(context_distribution),
            'semantic_version': self.semantic_engine.current_meaning_version
        }


class AlternativePathGenerator:
    """Generates alternative routing paths when primary paths fail"""
    
    def generate_alternatives(self, failed_path: List[str], 
                            topology: Dict[str, List[str]]) -> List[List[str]]:
        """Generate alternative paths avoiding failed nodes"""
        source = failed_path[0]
        target = failed_path[-1]
        failed_nodes = set(failed_path[1:-1])  # Exclude source and target
        
        # Create modified topology excluding failed nodes
        safe_topology = {}
        for node, neighbors in topology.items():
            if node not in failed_nodes:
                safe_neighbors = [n for n in neighbors if n not in failed_nodes]
                safe_topology[node] = safe_neighbors
        
        # Find paths in safe topology
        return self._find_paths_avoiding_nodes(source, target, safe_topology, failed_nodes)
    
    def _find_paths_avoiding_nodes(self, source: str, target: str, 
                                 topology: Dict[str, List[str]], 
                                 avoid_nodes: Set[str]) -> List[List[str]]:
        """Find paths while avoiding specific nodes"""
        paths = []
        
        def dfs(current_path: List[str], visited: Set[str]):
            current = current_path[-1]
            
            if current == target:
                paths.append(current_path.copy())
                return
            
            if len(current_path) > 6:  # Limit path length
                return
            
            for neighbor in topology.get(current, []):
                if neighbor not in visited and neighbor not in avoid_nodes:
                    visited.add(neighbor)
                    current_path.append(neighbor)
                    dfs(current_path, visited)
                    current_path.pop()
                    visited.remove(neighbor)
        
        dfs([source], {source})
        return paths


# Integration with TCP Stealth Detection System
async def integrate_semantic_routing_with_detection(
    detection_events: List[Dict],
    semantic_engine: SemanticEvolutionEngine,
    router: AdaptiveSemanticRouter
) -> Dict[str, Any]:
    """
    Integration function that adapts semantic routing based on detection events.
    This connects with Elena's detection algorithms and Marcus's network adaptation.
    """
    adaptation_results = {
        'semantic_evolutions': 0,
        'routing_adaptations': 0,
        'network_meaning_changes': []
    }
    
    for event in detection_events:
        # Extract threat context from detection event
        threat_context = {
            'severity': event.get('confidence', 0.5),
            'type': event.get('compromise_type', 'unknown'),
            'compromised_nodes': [event.get('target_agent', '')],
            'evidence': event.get('evidence', [])
        }
        
        # Evolve semantics in response to threat
        evolution_result = await semantic_engine.evolve_semantics(threat_context)
        adaptation_results['semantic_evolutions'] += 1
        adaptation_results['network_meaning_changes'].append(evolution_result)
    
    return adaptation_results


if __name__ == "__main__":
    # Demo of semantic routing adaptation
    async def demo_semantic_adaptation():
        print("=== Semantic Routing Adaptation Demo ===")
        
        # Create semantic evolution engine
        semantic_engine = SemanticEvolutionEngine()
        router = AdaptiveSemanticRouter(semantic_engine)
        
        # Create sample network topology
        topology = {
            'agent_001': ['agent_002', 'agent_003'],
            'agent_002': ['agent_001', 'agent_004'],
            'agent_003': ['agent_001', 'agent_004'],
            'agent_004': ['agent_002', 'agent_003']
        }
        
        # Create a message to route
        message = SemanticMessage(
            message_id="test_msg_001",
            source="agent_001",
            target="agent_004",
            content={
                "command": "assess_risk",
                "trust_signals": {
                    "high_accuracy": 0.8,
                    "established_trust": 0.9
                }
            },
            semantic_context=SemanticContext.COMMAND_ASSESSMENT,
            trust_level_required=0.7
        )
        
        # Route message with current semantics
        print("\n1. Initial routing with baseline semantics:")
        initial_routing = await router.route_message(message, topology)
        print(f"   Chosen path: {initial_routing.chosen_path}")
        print(f"   Confidence: {initial_routing.confidence:.3f}")
        
        # Simulate threat detection
        threat_context = {
            'severity': 0.8,
            'type': 'semantic_hijack',
            'compromised_nodes': ['agent_002'],
            'evidence': ['systematic_bias_detected']
        }
        
        # Evolve semantics in response to threat
        print("\n2. Evolving semantics due to threat detection:")
        evolution_result = await semantic_engine.evolve_semantics(threat_context)
        print(f"   Strategy: {evolution_result['adaptation_strategy']}")
        print(f"   New meaning version: {evolution_result['new_meaning_version']}")
        
        # Route same message with evolved semantics
        print("\n3. Routing with evolved semantics:")
        adapted_routing = await router.route_message(message, topology)
        print(f"   New chosen path: {adapted_routing.chosen_path}")
        print(f"   New confidence: {adapted_routing.confidence:.3f}")
        print(f"   Reasoning: {adapted_routing.reasoning}")
        
        # Show routing statistics
        print("\n4. Routing Statistics:")
        stats = router.get_routing_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Run the demo
    asyncio.run(demo_semantic_adaptation())