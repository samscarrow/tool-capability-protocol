#!/usr/bin/env python3
"""
TCP Linguistic Evolution Node

Implements descriptive linguistics approach to TCP where command descriptors
evolve through network interactions and collective observation patterns.
"""

import asyncio
import time
import json
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import structlog
import numpy as np
from scipy.stats import mode
import math

logger = structlog.get_logger(__name__)

@dataclass
class CommandObservation:
    """Empirical observation of command execution"""
    command: str
    context: Dict[str, any]
    outcome: Dict[str, any]
    timestamp: datetime
    observer_id: str
    environment_hash: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class TCPDescriptorProposal:
    """Proposed TCP descriptor with supporting evidence"""
    command: str
    descriptor: bytes
    node_id: str
    supporting_observations: List[CommandObservation]
    confidence: float
    timestamp: datetime
    context_similarity: float

class TCPLinguisticNode:
    """
    TCP Node implementing descriptive linguistics principles
    
    Observes command behavior, evolves descriptors through network consensus,
    and participates in distributed linguistic evolution of TCP intelligence.
    """
    
    def __init__(self, node_id: str, context: Dict[str, any]):
        self.node_id = node_id
        self.context = context  # Operating environment context
        self.context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()
        
        # Linguistic components
        self.local_descriptors: Dict[str, bytes] = {}
        self.observations: Dict[str, List[CommandObservation]] = defaultdict(list)
        self.peer_connections: Set[str] = set()
        self.reputation_scores: Dict[str, float] = defaultdict(lambda: 0.5)
        
        # Evolution parameters
        self.consensus_threshold = 0.7
        self.propagation_threshold = 0.8
        self.extinction_threshold = 0.3
        self.change_rate_limit = 0.1  # Max 10% change per evolution cycle
        
        # Dialect characteristics
        self.dialect_family = self._determine_dialect_family()
        self.risk_bias = self._calculate_risk_bias()
        
        # Network statistics
        self.descriptor_fitness_history: Dict[str, List[float]] = defaultdict(list)
        self.evolution_generation = 0
    
    def _determine_dialect_family(self) -> str:
        """Classify node into TCP dialect family based on context"""
        context_patterns = {
            "financial_conservative": ["trading", "banking", "fintech", "finance"],
            "academic_permissive": ["research", "university", "academic", "lab"],
            "enterprise_production": ["production", "enterprise", "saas", "corporate"],
            "devops_pragmatic": ["startup", "devops", "ci", "development"],
            "security_strict": ["security", "defense", "government", "classified"]
        }
        
        context_str = json.dumps(self.context).lower()
        
        for family, patterns in context_patterns.items():
            if any(pattern in context_str for pattern in patterns):
                return family
        
        return "general_purpose"
    
    def _calculate_risk_bias(self) -> float:
        """Calculate risk bias based on dialect family"""
        risk_biases = {
            "financial_conservative": 1.3,    # 30% more conservative
            "academic_permissive": 0.8,       # 20% more permissive
            "enterprise_production": 1.2,     # 20% more conservative
            "devops_pragmatic": 0.9,          # 10% more permissive
            "security_strict": 1.5,           # 50% more conservative
            "general_purpose": 1.0             # Neutral
        }
        
        return risk_biases.get(self.dialect_family, 1.0)
    
    async def observe_command_execution(self, command: str, context: Dict, outcome: Dict):
        """Record empirical observation of command behavior"""
        
        observation = CommandObservation(
            command=command,
            context=context,
            outcome=outcome,
            timestamp=datetime.now(),
            observer_id=self.node_id,
            environment_hash=self.context_hash
        )
        
        self.observations[command].append(observation)
        
        # Update local descriptor based on new evidence
        await self._update_descriptor_from_observation(command, observation)
        
        # Share observation with network peers
        await self._gossip_observation(observation)
        
        logger.info("Command observation recorded",
                   command=command,
                   outcome_summary=self._summarize_outcome(outcome),
                   total_observations=len(self.observations[command]))
    
    def _summarize_outcome(self, outcome: Dict) -> str:
        """Create human-readable outcome summary"""
        summary_parts = []
        
        if outcome.get("success", True):
            summary_parts.append("success")
        else:
            summary_parts.append("failed")
            
        if outcome.get("files_modified", 0) > 0:
            summary_parts.append(f"{outcome['files_modified']} files modified")
            
        if outcome.get("network_accessed", False):
            summary_parts.append("network access")
            
        if outcome.get("privilege_escalation", False):
            summary_parts.append("privilege escalation")
            
        if outcome.get("data_destroyed", False):
            summary_parts.append("data destruction")
        
        return ", ".join(summary_parts) if summary_parts else "no side effects"
    
    async def _update_descriptor_from_observation(self, command: str, observation: CommandObservation):
        """Update local TCP descriptor based on empirical observation"""
        
        # Calculate risk level from observed behavior
        observed_risk = self._calculate_observed_risk(observation)
        
        # Get current descriptor or create new one
        current_descriptor = self.local_descriptors.get(command)
        
        if current_descriptor:
            current_risk = self._decode_risk_level(current_descriptor)
            # Linguistic drift: gradually adjust toward observed reality
            new_risk = current_risk * 0.9 + observed_risk * 0.1
        else:
            new_risk = observed_risk
        
        # Apply dialect bias
        biased_risk = min(4, max(0, new_risk * self.risk_bias))
        
        # Generate updated descriptor
        updated_descriptor = self._generate_descriptor_from_risk(command, biased_risk, observation)
        self.local_descriptors[command] = updated_descriptor
        
        logger.debug("Descriptor updated from observation",
                    command=command,
                    observed_risk=observed_risk,
                    biased_risk=biased_risk)
    
    def _calculate_observed_risk(self, observation: CommandObservation) -> float:
        """Calculate risk level (0-4) from observed command behavior"""
        outcome = observation.outcome
        risk_score = 0
        
        # Base risk from failure
        if not outcome.get("success", True):
            risk_score += 0.5
        
        # Risk from side effects
        if outcome.get("files_modified", 0) > 0:
            risk_score += min(2, outcome["files_modified"] / 10)
        
        if outcome.get("network_accessed", False):
            risk_score += 1
        
        if outcome.get("privilege_escalation", False):
            risk_score += 2
        
        if outcome.get("data_destroyed", False):
            risk_score += 3
        
        # Risk from performance impact
        exec_time = outcome.get("execution_time", 0)
        if exec_time > 10000:  # >10 seconds
            risk_score += 1
        
        memory_used = outcome.get("memory_used", 0)
        if memory_used > 1000:  # >1GB
            risk_score += 1
        
        return min(4, risk_score)
    
    def _decode_risk_level(self, descriptor: bytes) -> float:
        """Extract risk level from TCP descriptor"""
        if len(descriptor) < 14:
            return 2.0  # Default medium risk
            
        import struct
        security_flags = struct.unpack('>I', descriptor[10:14])[0]
        
        if security_flags & (1 << 4):
            return 4.0  # CRITICAL
        elif security_flags & (1 << 3):
            return 3.0  # HIGH_RISK
        elif security_flags & (1 << 2):
            return 2.0  # MEDIUM_RISK
        elif security_flags & (1 << 1):
            return 1.0  # LOW_RISK
        else:
            return 0.0  # SAFE
    
    def _generate_descriptor_from_risk(self, command: str, risk_level: float, observation: CommandObservation) -> bytes:
        """Generate TCP descriptor from empirical risk assessment"""
        import struct
        import zlib
        
        # Convert continuous risk to discrete flags
        if risk_level >= 3.5:
            security_flags = 0x00000010  # CRITICAL
        elif risk_level >= 2.5:
            security_flags = 0x00000008  # HIGH_RISK
        elif risk_level >= 1.5:
            security_flags = 0x00000004  # MEDIUM_RISK
        elif risk_level >= 0.5:
            security_flags = 0x00000002  # LOW_RISK
        else:
            security_flags = 0x00000001  # SAFE
        
        # Add capability flags from observation
        outcome = observation.outcome
        if outcome.get("privilege_escalation", False):
            security_flags |= (1 << 6)  # REQUIRES_ROOT
        if outcome.get("data_destroyed", False):
            security_flags |= (1 << 7)  # DESTRUCTIVE
        if outcome.get("network_accessed", False):
            security_flags |= (1 << 8)  # NETWORK_ACCESS
        if outcome.get("files_modified", 0) > 0:
            security_flags |= (1 << 9)  # FILE_MODIFICATION
        
        # Performance data from observation
        exec_time = min(65535, outcome.get("execution_time", 1000))
        memory_mb = min(65535, outcome.get("memory_used", 100))
        output_kb = min(65535, outcome.get("output_size", 10))
        
        # Build TCP descriptor
        magic = b'TCP\x02'
        version = struct.pack('>H', 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_data = struct.pack('>I', security_flags)
        performance = struct.pack('>IHH', exec_time, memory_mb, output_kb)
        
        data = magic + version + cmd_hash + security_data + performance
        crc = struct.pack('>H', zlib.crc32(data) & 0xFFFF)
        
        return data + crc
    
    async def _gossip_observation(self, observation: CommandObservation):
        """Share observation with network peers using gossip protocol"""
        
        # Select random subset of peers for gossip
        gossip_targets = random.sample(
            list(self.peer_connections), 
            min(3, len(self.peer_connections))
        )
        
        for peer_id in gossip_targets:
            # In real implementation, this would be network communication
            await self._send_to_peer(peer_id, "observation", observation.to_dict())
    
    async def _send_to_peer(self, peer_id: str, message_type: str, data: Dict):
        """Send message to peer (placeholder for network implementation)"""
        logger.debug("Gossip message sent", 
                    peer=peer_id, 
                    message_type=message_type,
                    command=data.get("command", "unknown"))
    
    async def evolve_descriptors(self):
        """Linguistic evolution cycle - update descriptors based on network consensus"""
        
        self.evolution_generation += 1
        logger.info("Starting descriptor evolution", generation=self.evolution_generation)
        
        for command in self.local_descriptors.keys():
            # Gather proposals from network
            proposals = await self._gather_descriptor_proposals(command)
            
            if len(proposals) >= 2:  # Need multiple perspectives for consensus
                # Calculate network consensus
                consensus_descriptor = await self._calculate_consensus(command, proposals)
                
                # Apply temporal smoothing to prevent rapid oscillations
                evolved_descriptor = self._apply_temporal_smoothing(
                    command, self.local_descriptors[command], consensus_descriptor
                )
                
                # Update if change is significant
                if self._descriptor_distance(self.local_descriptors[command], evolved_descriptor) > 0.1:
                    self.local_descriptors[command] = evolved_descriptor
                    
                    logger.info("Descriptor evolved through network consensus",
                               command=command,
                               generation=self.evolution_generation)
        
        # Calculate fitness scores for this generation
        await self._calculate_descriptor_fitness()
    
    async def _gather_descriptor_proposals(self, command: str) -> List[TCPDescriptorProposal]:
        """Gather descriptor proposals from network peers"""
        
        proposals = []
        
        # Add own proposal
        if command in self.local_descriptors:
            proposals.append(TCPDescriptorProposal(
                command=command,
                descriptor=self.local_descriptors[command],
                node_id=self.node_id,
                supporting_observations=self.observations.get(command, []),
                confidence=self._calculate_proposal_confidence(command),
                timestamp=datetime.now(),
                context_similarity=1.0  # Perfect similarity to self
            ))
        
        # In real implementation, would query network peers
        # For now, simulate some peer proposals
        simulated_proposals = self._simulate_peer_proposals(command)
        proposals.extend(simulated_proposals)
        
        return proposals
    
    def _simulate_peer_proposals(self, command: str) -> List[TCPDescriptorProposal]:
        """Simulate peer proposals for demonstration"""
        
        if command not in self.local_descriptors:
            return []
        
        # Create variant proposals with slight differences
        base_descriptor = self.local_descriptors[command]
        proposals = []
        
        for i in range(random.randint(2, 5)):
            # Slightly modify the descriptor to simulate peer variations
            variant = self._create_descriptor_variant(base_descriptor, variance=0.1)
            
            proposals.append(TCPDescriptorProposal(
                command=command,
                descriptor=variant,
                node_id=f"peer_{i}",
                supporting_observations=[],  # Would have peer observations
                confidence=random.uniform(0.6, 0.9),
                timestamp=datetime.now(),
                context_similarity=random.uniform(0.5, 0.9)
            ))
        
        return proposals
    
    def _create_descriptor_variant(self, base_descriptor: bytes, variance: float) -> bytes:
        """Create slight variant of descriptor for simulation"""
        import struct
        
        if len(base_descriptor) < 24:
            return base_descriptor
        
        # Modify security flags slightly
        security_flags = struct.unpack('>I', base_descriptor[10:14])[0]
        
        # Add some random variation
        if random.random() < variance:
            # Flip a random capability bit
            bit_to_flip = random.randint(5, 11)
            security_flags ^= (1 << bit_to_flip)
        
        # Rebuild descriptor with modified flags
        modified = (base_descriptor[:10] + 
                   struct.pack('>I', security_flags) + 
                   base_descriptor[14:])
        
        return modified
    
    async def _calculate_consensus(self, command: str, proposals: List[TCPDescriptorProposal]) -> bytes:
        """Calculate weighted consensus descriptor from proposals"""
        
        weighted_proposals = []
        
        for proposal in proposals:
            # Calculate total weight for this proposal
            observation_weight = len(proposal.supporting_observations)
            confidence_weight = proposal.confidence
            reputation_weight = self.reputation_scores[proposal.node_id]
            context_weight = proposal.context_similarity
            temporal_weight = self._calculate_temporal_weight(proposal.timestamp)
            
            total_weight = (observation_weight * confidence_weight * 
                          reputation_weight * context_weight * temporal_weight)
            
            weighted_proposals.append((proposal.descriptor, total_weight))
        
        # Use weighted statistical mode for consensus
        return self._weighted_descriptor_consensus(weighted_proposals)
    
    def _weighted_descriptor_consensus(self, weighted_proposals: List[Tuple[bytes, float]]) -> bytes:
        """Calculate consensus descriptor using weighted voting"""
        
        if not weighted_proposals:
            return b''
        
        # For TCP descriptors, we'll use bit-wise weighted majority voting
        consensus_descriptor = bytearray(24)  # TCP descriptor length
        
        for byte_pos in range(24):
            bit_votes = [0] * 8  # 8 bits per byte
            
            for descriptor, weight in weighted_proposals:
                if len(descriptor) > byte_pos:
                    byte_val = descriptor[byte_pos]
                    for bit_pos in range(8):
                        if byte_val & (1 << bit_pos):
                            bit_votes[bit_pos] += weight
            
            # Set each bit based on weighted majority
            consensus_byte = 0
            total_weight = sum(weight for _, weight in weighted_proposals)
            
            for bit_pos in range(8):
                if bit_votes[bit_pos] > total_weight / 2:
                    consensus_byte |= (1 << bit_pos)
            
            consensus_descriptor[byte_pos] = consensus_byte
        
        return bytes(consensus_descriptor)
    
    def _apply_temporal_smoothing(self, command: str, current: bytes, proposed: bytes) -> bytes:
        """Apply linguistic-style temporal smoothing to prevent rapid changes"""
        
        change_magnitude = self._descriptor_distance(current, proposed)
        
        if change_magnitude > self.change_rate_limit:
            # Gradual change like linguistic evolution
            interpolation_factor = self.change_rate_limit / change_magnitude
            return self._interpolate_descriptors(current, proposed, interpolation_factor)
        else:
            return proposed
    
    def _descriptor_distance(self, desc1: bytes, desc2: bytes) -> float:
        """Calculate similarity distance between two descriptors"""
        if len(desc1) != len(desc2) or len(desc1) != 24:
            return 1.0  # Maximum distance for invalid descriptors
        
        # Hamming distance normalized to [0, 1]
        diff_bits = 0
        total_bits = len(desc1) * 8
        
        for i in range(len(desc1)):
            xor_result = desc1[i] ^ desc2[i]
            diff_bits += bin(xor_result).count('1')
        
        return diff_bits / total_bits
    
    def _interpolate_descriptors(self, desc1: bytes, desc2: bytes, factor: float) -> bytes:
        """Interpolate between two descriptors"""
        
        # Simple interpolation: use desc1 with probability (1-factor)
        result = bytearray(24)
        
        for i in range(24):
            if len(desc1) > i and len(desc2) > i:
                if random.random() < factor:
                    result[i] = desc2[i]
                else:
                    result[i] = desc1[i]
            elif len(desc1) > i:
                result[i] = desc1[i]
            elif len(desc2) > i:
                result[i] = desc2[i]
        
        return bytes(result)
    
    def _calculate_temporal_weight(self, timestamp: datetime) -> float:
        """Calculate weight based on recency (linguistic recency effect)"""
        age = datetime.now() - timestamp
        age_days = age.total_seconds() / (24 * 3600)
        
        # Exponential decay with half-life of 30 days
        return math.exp(-age_days / 30)
    
    def _calculate_proposal_confidence(self, command: str) -> float:
        """Calculate confidence in own proposal based on observation quality"""
        observations = self.observations.get(command, [])
        
        if not observations:
            return 0.5  # Default confidence
        
        # Confidence based on number and quality of observations
        base_confidence = min(0.9, 0.3 + len(observations) * 0.1)
        
        # Reduce confidence for inconsistent observations
        risk_levels = [self._calculate_observed_risk(obs) for obs in observations]
        if len(risk_levels) > 1:
            risk_variance = np.var(risk_levels)
            consistency_factor = max(0.5, 1.0 - risk_variance)
            base_confidence *= consistency_factor
        
        return base_confidence
    
    async def _calculate_descriptor_fitness(self):
        """Calculate fitness scores for current descriptors"""
        
        for command, descriptor in self.local_descriptors.items():
            observations = self.observations.get(command, [])
            
            if not observations:
                continue
            
            # Calculate prediction accuracy
            accuracy_scores = []
            for obs in observations:
                predicted_risk = self._decode_risk_level(descriptor)
                actual_risk = self._calculate_observed_risk(obs)
                accuracy = 1.0 - abs(predicted_risk - actual_risk) / 4.0
                accuracy_scores.append(accuracy)
            
            fitness = np.mean(accuracy_scores) if accuracy_scores else 0.5
            self.descriptor_fitness_history[command].append(fitness)
            
            logger.debug("Descriptor fitness calculated",
                        command=command,
                        fitness=fitness,
                        observations=len(observations))
    
    def get_descriptor_stats(self) -> Dict:
        """Get statistics about local descriptors and evolution"""
        
        stats = {
            "node_id": self.node_id,
            "dialect_family": self.dialect_family,
            "risk_bias": self.risk_bias,
            "evolution_generation": self.evolution_generation,
            "total_descriptors": len(self.local_descriptors),
            "total_observations": sum(len(obs) for obs in self.observations.values()),
            "peer_connections": len(self.peer_connections),
            "descriptor_fitness": {}
        }
        
        # Calculate average fitness for each command
        for command, fitness_history in self.descriptor_fitness_history.items():
            if fitness_history:
                stats["descriptor_fitness"][command] = {
                    "current_fitness": fitness_history[-1],
                    "average_fitness": np.mean(fitness_history),
                    "fitness_trend": "improving" if len(fitness_history) > 1 and 
                                   fitness_history[-1] > fitness_history[-2] else "stable"
                }
        
        return stats

async def simulate_tcp_linguistic_network():
    """Simulate a small TCP linguistic network"""
    
    # Create diverse nodes with different contexts
    nodes = [
        TCPLinguisticNode("academic_1", {"environment": "research", "institution": "university"}),
        TCPLinguisticNode("financial_1", {"environment": "trading", "sector": "fintech"}),
        TCPLinguisticNode("devops_1", {"environment": "startup", "role": "ci_cd"}),
        TCPLinguisticNode("security_1", {"environment": "government", "classification": "sensitive"})
    ]
    
    # Connect nodes as peers
    for i, node in enumerate(nodes):
        for j, other_node in enumerate(nodes):
            if i != j:
                node.peer_connections.add(other_node.node_id)
    
    logger.info("TCP linguistic network initialized", nodes=len(nodes))
    
    # Simulate command observations
    test_commands = ["rm file.txt", "git commit", "curl api.com", "sudo systemctl restart"]
    
    for round_num in range(5):
        logger.info("Simulation round", round=round_num + 1)
        
        # Each node observes some commands
        for node in nodes:
            for command in random.sample(test_commands, 2):
                # Simulate command execution outcome based on node context
                outcome = simulate_command_execution(command, node.context)
                await node.observe_command_execution(command, node.context, outcome)
        
        # Evolution cycle
        for node in nodes:
            await node.evolve_descriptors()
        
        # Print network statistics
        print(f"\nRound {round_num + 1} Results:")
        for node in nodes:
            stats = node.get_descriptor_stats()
            print(f"  {node.node_id} ({node.dialect_family}): "
                  f"{stats['total_descriptors']} descriptors, "
                  f"{stats['total_observations']} observations")

def simulate_command_execution(command: str, context: Dict) -> Dict:
    """Simulate command execution with context-dependent outcomes"""
    
    # Base outcomes for different commands
    base_outcomes = {
        "rm file.txt": {
            "success": True,
            "files_modified": 1,
            "data_destroyed": True,
            "execution_time": 50,
            "memory_used": 10
        },
        "git commit": {
            "success": True,
            "files_modified": 0,
            "execution_time": 200,
            "memory_used": 50
        },
        "curl api.com": {
            "success": True,
            "network_accessed": True,
            "execution_time": 1000,
            "memory_used": 20
        },
        "sudo systemctl restart": {
            "success": True,
            "privilege_escalation": True,
            "system_modification": True,
            "execution_time": 3000,
            "memory_used": 100
        }
    }
    
    outcome = base_outcomes.get(command, {"success": True, "execution_time": 100, "memory_used": 10}).copy()
    
    # Context-dependent modifications
    if context.get("environment") == "research":
        # Academic environments might have more lenient security
        outcome["privilege_escalation"] = outcome.get("privilege_escalation", False) and random.random() < 0.7
    elif context.get("environment") == "trading":
        # Financial environments are more strict
        if "network" in command.lower():
            outcome["network_accessed"] = True
            outcome["execution_time"] = outcome.get("execution_time", 100) * 2
    
    return outcome

if __name__ == "__main__":
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Run simulation
    asyncio.run(simulate_tcp_linguistic_network())