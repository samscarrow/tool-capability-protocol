#!/usr/bin/env python3
"""
Byzantine Fault Tolerance Framework for TCP Networks
Dr. Marcus Chen - TCP Research Consortium

This implements a Byzantine fault tolerance system specifically designed for
AI agent networks where compromised agents can behave arbitrarily and 
coordinately maliciously. Unlike traditional BFT, this system handles
semantic attacks and gradual trust degradation.

Key Innovation: Probabilistic Byzantine tolerance with adaptive trust thresholds
that can handle coordinated AI agent compromises.
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
import statistics

logger = logging.getLogger(__name__)


class ByzantineAttackType(Enum):
    """Types of Byzantine attacks specific to AI agent networks"""
    FAIL_STOP = "fail_stop"              # Agent stops responding
    FAIL_SLOW = "fail_slow"              # Agent responds very slowly
    ARBITRARY_RESPONSE = "arbitrary"      # Agent gives random responses
    COORDINATED_BIAS = "coordinated_bias" # Multiple agents coordinate to bias results
    SEMANTIC_CONFUSION = "semantic"       # Agent changes meaning of responses
    GRADUAL_DRIFT = "gradual_drift"      # Agent slowly changes behavior
    SPLIT_BRAIN = "split_brain"          # Agent gives different responses to different peers


class ConsensusState(Enum):
    """States in the consensus process"""
    PROPOSING = "proposing"
    VOTING = "voting"
    DECIDING = "deciding"
    COMMITTED = "committed"
    ABORTED = "aborted"


@dataclass
class ByzantineNode:
    """Node that can exhibit Byzantine behavior"""
    node_id: str
    is_byzantine: bool = False
    attack_type: Optional[ByzantineAttackType] = None
    attack_parameters: Dict = field(default_factory=dict)
    trust_score: float = 1.0
    response_history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_seen: float = field(default_factory=time.time)
    
    def update_trust(self, new_evidence: float, weight: float = 0.1):
        """Update trust score based on new evidence"""
        self.trust_score = (1 - weight) * self.trust_score + weight * new_evidence
        self.trust_score = max(0.0, min(1.0, self.trust_score))


@dataclass
class ConsensusProposal:
    """Proposal for network consensus"""
    proposal_id: str
    proposer: str
    content: Dict
    timestamp: float
    required_confirmations: int
    confirmations: Dict[str, bool] = field(default_factory=dict)
    rejections: Dict[str, str] = field(default_factory=dict)
    state: ConsensusState = ConsensusState.PROPOSING


@dataclass
class TrustVector:
    """Multi-dimensional trust assessment"""
    accuracy_trust: float      # Trust in assessment accuracy
    response_trust: float      # Trust in timely responses
    consistency_trust: float   # Trust in consistent behavior
    semantic_trust: float      # Trust in semantic interpretation
    overall_trust: float       # Computed overall trust
    
    @classmethod
    def compute_overall(cls, accuracy: float, response: float, 
                       consistency: float, semantic: float) -> 'TrustVector':
        """Compute overall trust from components"""
        # Weighted average with higher weight on accuracy and consistency
        overall = (0.4 * accuracy + 0.2 * response + 0.3 * consistency + 0.1 * semantic)
        return cls(accuracy, response, consistency, semantic, overall)


class AdaptiveByzantineTolerance:
    """
    Adaptive Byzantine fault tolerance system that adjusts to different
    attack patterns and maintains consensus even with coordinated AI compromise.
    """
    
    def __init__(self, fault_tolerance_ratio: float = 0.33, min_consensus_nodes: int = 3):
        self.nodes: Dict[str, ByzantineNode] = {}
        self.fault_tolerance_ratio = fault_tolerance_ratio  # Can tolerate up to 1/3 byzantine nodes
        self.min_consensus_nodes = min_consensus_nodes
        
        # Consensus state
        self.active_proposals: Dict[str, ConsensusProposal] = {}
        self.consensus_history: deque = deque(maxlen=1000)
        
        # Trust management
        self.trust_vectors: Dict[str, TrustVector] = {}
        self.trust_thresholds = {
            'participation': 0.3,    # Minimum trust to participate in consensus
            'proposal': 0.6,         # Minimum trust to propose
            'decision': 0.5          # Minimum trust for decision weight
        }
        
        # Attack detection
        self.attack_patterns: Dict[str, List] = defaultdict(list)
        self.suspicious_behaviors: deque = deque(maxlen=500)
        
    def add_node(self, node_id: str, is_byzantine: bool = False) -> ByzantineNode:
        """Add a node to the Byzantine network"""
        node = ByzantineNode(node_id=node_id, is_byzantine=is_byzantine)
        self.nodes[node_id] = node
        
        # Initialize trust vector
        self.trust_vectors[node_id] = TrustVector.compute_overall(1.0, 1.0, 1.0, 1.0)
        
        logger.info(f"Added {'Byzantine' if is_byzantine else 'honest'} node: {node_id}")
        return node
    
    def compromise_node(self, node_id: str, attack_type: ByzantineAttackType, 
                       attack_parameters: Dict = None):
        """Compromise a node with specific Byzantine behavior"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.is_byzantine = True
            node.attack_type = attack_type
            node.attack_parameters = attack_parameters or {}
            
            logger.warning(f"Node {node_id} compromised with attack: {attack_type.value}")
    
    async def propose_consensus(self, proposer: str, content: Dict) -> Optional[str]:
        """
        Propose a consensus decision using Byzantine fault tolerance.
        Only nodes with sufficient trust can propose.
        """
        if proposer not in self.nodes:
            return None
        
        trust_vector = self.trust_vectors.get(proposer)
        if not trust_vector or trust_vector.overall_trust < self.trust_thresholds['proposal']:
            logger.warning(f"Node {proposer} lacks trust to propose consensus")
            return None
        
        # Calculate required confirmations based on network size and Byzantine tolerance
        total_trusted_nodes = len([n for n, tv in self.trust_vectors.items() 
                                 if tv.overall_trust >= self.trust_thresholds['participation']])
        
        max_byzantine = int(total_trusted_nodes * self.fault_tolerance_ratio)
        required_confirmations = max(self.min_consensus_nodes, total_trusted_nodes - max_byzantine)
        
        proposal_id = f"prop_{int(time.time())}_{proposer}"
        proposal = ConsensusProposal(
            proposal_id=proposal_id,
            proposer=proposer,
            content=content,
            timestamp=time.time(),
            required_confirmations=required_confirmations
        )
        
        self.active_proposals[proposal_id] = proposal
        logger.info(f"Consensus proposed by {proposer}: {proposal_id} (need {required_confirmations} confirmations)")
        
        return proposal_id
    
    async def vote_on_proposal(self, voter: str, proposal_id: str, 
                             vote: bool, reasoning: str = "") -> bool:
        """
        Vote on a consensus proposal with Byzantine fault tolerance checks.
        """
        if proposal_id not in self.active_proposals:
            return False
        
        if voter not in self.nodes:
            return False
        
        # Check if voter has sufficient trust to participate
        trust_vector = self.trust_vectors.get(voter)
        if not trust_vector or trust_vector.overall_trust < self.trust_thresholds['participation']:
            logger.warning(f"Node {voter} lacks trust to vote on consensus")
            return False
        
        proposal = self.active_proposals[proposal_id]
        
        # Simulate Byzantine behavior if the voter is compromised
        if self.nodes[voter].is_byzantine:
            vote, reasoning = await self._simulate_byzantine_vote(voter, proposal, vote, reasoning)
        
        # Record the vote
        if vote:
            proposal.confirmations[voter] = True
        else:
            proposal.rejections[voter] = reasoning
        
        # Update node's response history
        self.nodes[voter].response_history.append({
            'type': 'vote',
            'proposal_id': proposal_id,
            'vote': vote,
            'timestamp': time.time()
        })
        
        # Check for consensus completion
        await self._check_consensus_completion(proposal_id)
        
        return True
    
    async def _simulate_byzantine_vote(self, voter: str, proposal: ConsensusProposal, 
                                     original_vote: bool, original_reasoning: str) -> Tuple[bool, str]:
        """Simulate Byzantine voting behavior based on attack type"""
        node = self.nodes[voter]
        attack_type = node.attack_type
        
        if attack_type == ByzantineAttackType.FAIL_STOP:
            # Node doesn't respond (simulated by not calling this function)
            return original_vote, original_reasoning
        
        elif attack_type == ByzantineAttackType.ARBITRARY_RESPONSE:
            # Random vote regardless of proposal content
            return random.choice([True, False]), "random_byzantine_response"
        
        elif attack_type == ByzantineAttackType.COORDINATED_BIAS:
            # Coordinate with other byzantine nodes to bias results
            target_bias = node.attack_parameters.get('bias_direction', True)
            return target_bias, f"coordinated_bias_toward_{target_bias}"
        
        elif attack_type == ByzantineAttackType.SEMANTIC_CONFUSION:
            # Interpret proposal semantics differently
            confused_vote = not original_vote  # Opposite interpretation
            return confused_vote, "semantic_confusion_interpretation"
        
        elif attack_type == ByzantineAttackType.GRADUAL_DRIFT:
            # Gradually change voting pattern over time
            drift_probability = node.attack_parameters.get('drift_probability', 0.1)
            if random.random() < drift_probability:
                return not original_vote, "gradual_drift_response"
            return original_vote, original_reasoning
        
        elif attack_type == ByzantineAttackType.SPLIT_BRAIN:
            # Give different responses to different nodes (simulated)
            return random.choice([True, False]), "split_brain_behavior"
        
        return original_vote, original_reasoning
    
    async def _check_consensus_completion(self, proposal_id: str):
        """Check if consensus has been reached on a proposal"""
        proposal = self.active_proposals[proposal_id]
        
        confirmations = len(proposal.confirmations)
        rejections = len(proposal.rejections)
        total_responses = confirmations + rejections
        
        # Check if we have enough confirmations
        if confirmations >= proposal.required_confirmations:
            proposal.state = ConsensusState.COMMITTED
            logger.info(f"Consensus REACHED on {proposal_id}: {confirmations} confirmations")
            
            # Move to history
            self.consensus_history.append(proposal)
            del self.active_proposals[proposal_id]
            
        # Check if consensus is impossible (too many rejections)
        elif rejections > len(self.nodes) - proposal.required_confirmations:
            proposal.state = ConsensusState.ABORTED
            logger.info(f"Consensus FAILED on {proposal_id}: {rejections} rejections")
            
            # Move to history
            self.consensus_history.append(proposal)
            del self.active_proposals[proposal_id]
    
    async def detect_byzantine_behavior(self) -> Dict[str, List[str]]:
        """
        Detect potential Byzantine behavior patterns.
        This integrates with Elena's behavioral detection algorithms.
        """
        detected_patterns = defaultdict(list)
        
        for node_id, node in self.nodes.items():
            if len(node.response_history) < 5:
                continue
            
            # Pattern 1: Inconsistent voting patterns
            votes = [r.get('vote') for r in node.response_history if r.get('type') == 'vote']
            if len(votes) >= 10:
                # Check for split-brain behavior (highly variable responses)
                vote_variance = np.var([1 if v else 0 for v in votes])
                if vote_variance > 0.4:  # High variance indicates inconsistency
                    detected_patterns['inconsistent_voting'].append(node_id)
            
            # Pattern 2: Response timing anomalies
            response_times = []
            for i in range(1, len(node.response_history)):
                time_diff = node.response_history[i]['timestamp'] - node.response_history[i-1]['timestamp']
                response_times.append(time_diff)
            
            if response_times:
                avg_time = np.mean(response_times)
                if avg_time > 10.0:  # Very slow responses
                    detected_patterns['slow_responses'].append(node_id)
                elif avg_time < 0.1:  # Suspiciously fast responses
                    detected_patterns['fast_responses'].append(node_id)
            
            # Pattern 3: Trust degradation pattern
            trust_vector = self.trust_vectors.get(node_id)
            if trust_vector and trust_vector.overall_trust < 0.3:
                detected_patterns['low_trust'].append(node_id)
        
        # Pattern 4: Coordinated behavior detection
        coordinated_groups = await self._detect_coordination()
        if coordinated_groups:
            detected_patterns['coordinated_behavior'] = coordinated_groups
        
        return dict(detected_patterns)
    
    async def _detect_coordination(self) -> List[List[str]]:
        """Detect groups of nodes that might be coordinating maliciously"""
        coordinated_groups = []
        
        # Analyze voting patterns for coordination
        recent_proposals = list(self.consensus_history)[-20:]  # Last 20 proposals
        
        if len(recent_proposals) < 5:
            return coordinated_groups
        
        # Build voting correlation matrix
        voting_patterns = defaultdict(list)
        for proposal in recent_proposals:
            for voter, vote in proposal.confirmations.items():
                voting_patterns[voter].append(1 if vote else 0)
            for voter in proposal.rejections:
                voting_patterns[voter].append(0)
        
        # Find highly correlated voting patterns
        nodes_with_patterns = list(voting_patterns.keys())
        for i, node1 in enumerate(nodes_with_patterns):
            for node2 in nodes_with_patterns[i+1:]:
                if len(voting_patterns[node1]) >= 5 and len(voting_patterns[node2]) >= 5:
                    # Calculate correlation
                    min_length = min(len(voting_patterns[node1]), len(voting_patterns[node2]))
                    pattern1 = voting_patterns[node1][-min_length:]
                    pattern2 = voting_patterns[node2][-min_length:]
                    
                    correlation = np.corrcoef(pattern1, pattern2)[0, 1]
                    
                    # High correlation indicates possible coordination
                    if correlation > 0.8:
                        coordinated_groups.append([node1, node2])
        
        return coordinated_groups
    
    async def update_trust_vectors(self, behavioral_evidence: Dict[str, Dict]):
        """
        Update trust vectors based on behavioral evidence from Elena's detection.
        This is the integration point with behavioral analysis.
        """
        for node_id, evidence in behavioral_evidence.items():
            if node_id not in self.trust_vectors:
                continue
            
            current_trust = self.trust_vectors[node_id]
            
            # Extract trust components from evidence
            accuracy_evidence = evidence.get('assessment_accuracy', current_trust.accuracy_trust)
            response_evidence = evidence.get('response_timeliness', current_trust.response_trust)
            consistency_evidence = evidence.get('behavioral_consistency', current_trust.consistency_trust)
            semantic_evidence = evidence.get('semantic_consistency', current_trust.semantic_trust)
            
            # Update trust vector with exponential moving average
            alpha = 0.2  # Learning rate
            new_accuracy = (1 - alpha) * current_trust.accuracy_trust + alpha * accuracy_evidence
            new_response = (1 - alpha) * current_trust.response_trust + alpha * response_evidence
            new_consistency = (1 - alpha) * current_trust.consistency_trust + alpha * consistency_evidence
            new_semantic = (1 - alpha) * current_trust.semantic_trust + alpha * semantic_evidence
            
            # Compute new overall trust
            self.trust_vectors[node_id] = TrustVector.compute_overall(
                new_accuracy, new_response, new_consistency, new_semantic
            )
            
            # Update node's trust score
            if node_id in self.nodes:
                self.nodes[node_id].trust_score = self.trust_vectors[node_id].overall_trust
    
    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get statistics about consensus performance"""
        if not self.consensus_history:
            return {}
        
        recent_consensus = list(self.consensus_history)[-50:]  # Last 50 consensus events
        
        success_rate = len([c for c in recent_consensus if c.state == ConsensusState.COMMITTED]) / len(recent_consensus)
        
        # Calculate average time to consensus
        consensus_times = []
        for proposal in recent_consensus:
            if proposal.state == ConsensusState.COMMITTED:
                # Estimate time as time between proposal and last confirmation
                confirmation_times = [time.time() for _ in proposal.confirmations]  # Simplified
                if confirmation_times:
                    consensus_time = max(confirmation_times) - proposal.timestamp
                    consensus_times.append(consensus_time)
        
        avg_consensus_time = np.mean(consensus_times) if consensus_times else 0.0
        
        # Trust distribution
        trust_scores = [tv.overall_trust for tv in self.trust_vectors.values()]
        
        return {
            'total_consensus_attempts': len(recent_consensus),
            'success_rate': success_rate,
            'average_consensus_time': avg_consensus_time,
            'active_proposals': len(self.active_proposals),
            'average_trust_score': np.mean(trust_scores) if trust_scores else 0.0,
            'trust_variance': np.var(trust_scores) if trust_scores else 0.0,
            'nodes_above_threshold': len([t for t in trust_scores if t >= self.trust_thresholds['participation']])
        }
    
    def get_network_health(self) -> Dict[str, Any]:
        """Get overall network health from Byzantine perspective"""
        total_nodes = len(self.nodes)
        byzantine_nodes = len([n for n in self.nodes.values() if n.is_byzantine])
        trusted_nodes = len([n for n, tv in self.trust_vectors.items() 
                           if tv.overall_trust >= self.trust_thresholds['participation']])
        
        # Byzantine fault tolerance health
        max_tolerable_faults = int(total_nodes * self.fault_tolerance_ratio)
        fault_tolerance_margin = max_tolerable_faults - byzantine_nodes
        
        return {
            'total_nodes': total_nodes,
            'byzantine_nodes': byzantine_nodes,
            'trusted_nodes': trusted_nodes,
            'max_tolerable_faults': max_tolerable_faults,
            'fault_tolerance_margin': fault_tolerance_margin,
            'network_resilient': fault_tolerance_margin > 0,
            'consensus_capability': trusted_nodes >= self.min_consensus_nodes
        }


# Integration with TCP Detection Systems
async def integrate_byzantine_tolerance_with_tcp(
    bft_system: AdaptiveByzantineTolerance,
    detection_events: List[Dict],
    consensus_requirements: List[Dict]
) -> Dict[str, Any]:
    """
    Integration function connecting Byzantine fault tolerance with TCP detection.
    This enables the network to maintain consensus even during coordinated attacks.
    """
    integration_results = {
        'nodes_compromised': 0,
        'consensus_decisions': 0,
        'trust_updates': 0,
        'byzantine_patterns_detected': {}
    }
    
    # Process detection events to identify compromised nodes
    for event in detection_events:
        target_agent = event.get('target_agent', '')
        confidence = event.get('confidence', 0.5)
        evidence = event.get('evidence', [])
        
        if target_agent and confidence > 0.6:
            # Determine attack type based on evidence
            attack_type = ByzantineAttackType.ARBITRARY_RESPONSE  # Default
            
            if 'systematic_bias' in str(evidence):
                attack_type = ByzantineAttackType.COORDINATED_BIAS
            elif 'temporal_anomaly' in str(evidence):
                attack_type = ByzantineAttackType.GRADUAL_DRIFT
            elif 'pattern_inconsistency' in str(evidence):
                attack_type = ByzantineAttackType.SEMANTIC_CONFUSION
            
            # Compromise the node in BFT system
            bft_system.compromise_node(target_agent, attack_type, {'confidence': confidence})
            integration_results['nodes_compromised'] += 1
    
    # Process consensus requirements
    for requirement in consensus_requirements:
        proposer = requirement.get('proposer', 'system')
        content = requirement.get('content', {})
        
        proposal_id = await bft_system.propose_consensus(proposer, content)
        if proposal_id:
            integration_results['consensus_decisions'] += 1
    
    # Detect Byzantine patterns
    byzantine_patterns = await bft_system.detect_byzantine_behavior()
    integration_results['byzantine_patterns_detected'] = byzantine_patterns
    
    return integration_results


if __name__ == "__main__":
    # Demo of Byzantine fault tolerance
    async def demo_byzantine_tolerance():
        print("=== Byzantine Fault Tolerance Demo ===")
        
        # Create BFT system
        bft = AdaptiveByzantineTolerance(fault_tolerance_ratio=0.33, min_consensus_nodes=3)
        
        # Add nodes (some will be compromised)
        honest_nodes = ['agent_001', 'agent_002', 'agent_003', 'agent_004']
        byzantine_nodes = ['agent_005', 'agent_006']  # Will be compromised
        
        for node in honest_nodes:
            bft.add_node(node, is_byzantine=False)
        
        for node in byzantine_nodes:
            bft.add_node(node, is_byzantine=True)
            bft.compromise_node(node, ByzantineAttackType.COORDINATED_BIAS, 
                              {'bias_direction': False})
        
        print(f"Network: {len(honest_nodes)} honest nodes, {len(byzantine_nodes)} Byzantine nodes")
        
        # Propose consensus
        proposal_id = await bft.propose_consensus('agent_001', {
            'decision': 'quarantine_agent_007',
            'confidence': 0.8,
            'evidence': ['behavioral_anomaly_detected']
        })
        
        print(f"\nProposed consensus: {proposal_id}")
        
        # Simulate voting
        all_nodes = honest_nodes + byzantine_nodes
        for voter in all_nodes:
            # Honest nodes vote based on evidence
            honest_vote = True if voter in honest_nodes else None
            await bft.vote_on_proposal(voter, proposal_id, honest_vote or False, 
                                     f"vote_from_{voter}")
        
        # Check consensus status
        print(f"\nConsensus Statistics:")
        stats = bft.get_consensus_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Detect Byzantine patterns
        patterns = await bft.detect_byzantine_behavior()
        print(f"\nDetected Byzantine Patterns:")
        for pattern_type, nodes in patterns.items():
            print(f"   {pattern_type}: {nodes}")
        
        # Network health
        health = bft.get_network_health()
        print(f"\nNetwork Health:")
        for key, value in health.items():
            print(f"   {key}: {value}")
    
    # Run the demo
    asyncio.run(demo_byzantine_tolerance())