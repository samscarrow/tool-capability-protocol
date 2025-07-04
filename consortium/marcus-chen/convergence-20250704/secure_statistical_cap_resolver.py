#!/usr/bin/env python3
"""
Security-Hardened Statistical CAP Theorem Resolver
Dr. Marcus Chen & Dr. Aria Blackwood - TCP Research Consortium
Convergence Session: CONVERGENCE-20250704 + Security Hardening

This resolver addresses temporal coordination attacks on the statistical CAP theorem
implementation while maintaining bounded staleness with statistical guarantees.
Prevents exploitation of predictable staleness windows and partition attack vectors.

Key Security Enhancements:
- Randomized staleness bounds to prevent timing attacks
- Cryptographic timestamping to prevent temporal forgery
- Partition-resistant consensus with adaptive thresholds
- Jittered consistency recovery to avoid coordinated exploitation
"""

import asyncio
import time
import numpy as np
import secrets
import random
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from collections import defaultdict, deque
import uuid
from abc import ABC, abstractmethod
import hashlib

# Cryptographic imports for security hardening
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
except ImportError:
    print("Warning: cryptography package not available. Using mock signatures for development.")
    
    class MockEd25519PrivateKey:
        @classmethod
        def generate(cls): return cls()
        def sign(self, data): return b"mock_signature_" + data[:16]
        def public_key(self): return MockEd25519PublicKey()
    
    class MockEd25519PublicKey:
        def verify(self, signature, data): return True
    
    Ed25519PrivateKey = MockEd25519PrivateKey
    Ed25519PublicKey = MockEd25519PublicKey
    InvalidSignature = Exception

logger = logging.getLogger(__name__)


class ConsistencyLevel(Enum):
    """Consistency levels for statistical data"""
    IMMEDIATE = "immediate"          # Strong consistency requirement
    BOUNDED_STALENESS = "bounded"    # Bounded staleness tolerance
    EVENTUAL = "eventual"           # Eventual consistency acceptable
    WEAK = "weak"                   # Weak consistency (best effort)


class StatisticalDataType(Enum):
    """Types of statistical data with randomized staleness bounds (security hardening)"""
    BEHAVIORAL_BASELINE = "baseline"         # Randomized staleness: 3-7 seconds
    ANOMALY_DETECTION = "anomaly"           # Randomized staleness: 0.5-1.5 seconds  
    CORRELATION_MATRIX = "correlation"      # Randomized staleness: 10-30 seconds
    CONFIDENCE_INTERVALS = "confidence"     # Randomized staleness: 2-8 seconds
    POPULATION_STATISTICS = "population"    # Randomized staleness: 15-45 seconds


class NetworkPartitionState(Enum):
    """States of network partitions with enhanced security monitoring"""
    FULLY_CONNECTED = "connected"
    MINOR_PARTITION = "minor_partition"     # <20% nodes partitioned
    MAJOR_PARTITION = "major_partition"     # 20-50% nodes partitioned  
    SEVERE_PARTITION = "severe_partition"   # >50% nodes partitioned
    NETWORK_SPLIT = "split"                # Multiple equal-sized partitions
    ATTACK_SUSPECTED = "attack_suspected"   # Partition patterns suggest attack


@dataclass
class CryptographicTimestamp:
    """Cryptographically secure timestamp to prevent temporal forgery"""
    logical_time: int
    wall_clock: float
    node_id: str
    signature: bytes = field(default=b"")
    nonce: bytes = field(default_factory=lambda: secrets.token_bytes(16))
    
    def sign_timestamp(self, private_key: Ed25519PrivateKey) -> None:
        """Sign timestamp with node's private key"""
        timestamp_data = f"{self.logical_time}:{self.wall_clock}:{self.node_id}:{self.nonce.hex()}"
        self.signature = private_key.sign(timestamp_data.encode())
    
    def verify_timestamp(self, public_key: Ed25519PublicKey) -> bool:
        """Verify cryptographic authenticity of timestamp"""
        try:
            timestamp_data = f"{self.logical_time}:{self.wall_clock}:{self.node_id}:{self.nonce.hex()}"
            public_key.verify(self.signature, timestamp_data.encode())
            return True
        except (InvalidSignature, Exception):
            return False


@dataclass
class SecureStatisticalData:
    """Statistical data with cryptographic security and randomized staleness"""
    data_id: str
    data_type: StatisticalDataType
    content: Dict[str, Any]
    secure_timestamp: CryptographicTimestamp
    version: int
    source_node: str
    
    # Security-enhanced consistency metadata
    consistency_requirement: ConsistencyLevel
    base_staleness_bound: float  # Base staleness before randomization
    actual_staleness_bound: float  # Randomized staleness bound
    accuracy_tolerance: float
    
    # Cryptographic integrity
    content_signature: bytes = field(default=b"")
    content_hash: str = field(default="")
    
    # Enhanced vector clock for causal ordering
    secure_vector_clock: Dict[str, CryptographicTimestamp] = field(default_factory=dict)
    
    # Enhanced partition tolerance
    partition_tolerant: bool = True
    requires_supermajority: bool = False  # Requires >67% consensus during partitions
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._compute_content_hash()
        # Randomize staleness bound for security (±50% jitter)
        if self.actual_staleness_bound == 0:
            jitter_factor = 0.5 + random.random()  # 0.5 to 1.5 multiplier
            self.actual_staleness_bound = self.base_staleness_bound * jitter_factor
    
    def _compute_content_hash(self) -> str:
        """Compute SHA-256 hash of statistical content"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def sign_content(self, private_key: Ed25519PrivateKey) -> None:
        """Sign statistical content with source node's private key"""
        content_data = f"{self.data_id}:{self.content_hash}:{self.source_node}:{self.version}"
        self.content_signature = private_key.sign(content_data.encode())
    
    def verify_integrity(self, public_key: Ed25519PublicKey) -> bool:
        """Verify cryptographic integrity of statistical data"""
        try:
            # Verify content hash
            if self.content_hash != self._compute_content_hash():
                return False
            
            # Verify content signature
            content_data = f"{self.data_id}:{self.content_hash}:{self.source_node}:{self.version}"
            public_key.verify(self.content_signature, content_data.encode())
            
            # Verify timestamp signature
            if not self.secure_timestamp.verify_timestamp(public_key):
                return False
            
            return True
        except (InvalidSignature, Exception):
            return False
    
    def is_stale_with_jitter(self, current_time: float) -> bool:
        """Check staleness with randomized bound to prevent timing attacks"""
        age = current_time - self.secure_timestamp.wall_clock
        return age > self.actual_staleness_bound


class SecureStatisticalCAPResolver:
    """
    Security-hardened CAP theorem resolver with temporal attack prevention:
    - Randomized staleness bounds prevent timing attacks
    - Cryptographic timestamps prevent temporal forgery
    - Adaptive consistency thresholds during partitions
    - Jittered recovery to prevent coordinated exploitation
    """
    
    def __init__(self):
        # Enhanced security parameters
        self.randomize_staleness = True
        self.max_staleness_jitter = 0.5  # ±50% randomization
        self.partition_detection_threshold = 3  # Require 3 consistent readings
        
        # Cryptographic infrastructure
        self.node_private_keys: Dict[str, Ed25519PrivateKey] = {}
        self.node_public_keys: Dict[str, Ed25519PublicKey] = {}
        
        # Core CAP resolver state
        self.nodes: Set[str] = set()
        self.partitions: List[Set[str]] = []
        self.current_partition_state = NetworkPartitionState.FULLY_CONNECTED
        
        # Secure data storage with jittered staleness
        self.statistical_data: Dict[str, SecureStatisticalData] = {}
        self.secure_vector_clocks: Dict[str, CryptographicTimestamp] = {}
        
        # Security-enhanced consistency management
        self.dynamic_staleness_bounds: Dict[StatisticalDataType, Tuple[float, float]] = {
            StatisticalDataType.ANOMALY_DETECTION: (0.5, 1.5),      # Randomized window
            StatisticalDataType.BEHAVIORAL_BASELINE: (3.0, 7.0),    # Randomized window
            StatisticalDataType.CONFIDENCE_INTERVALS: (2.0, 8.0),   # Randomized window
            StatisticalDataType.CORRELATION_MATRIX: (10.0, 30.0),   # Randomized window
            StatisticalDataType.POPULATION_STATISTICS: (15.0, 45.0) # Randomized window
        }
        
        # Partition attack detection
        self.partition_history: deque = deque(maxlen=100)
        self.suspicious_partition_patterns = 0
        self.coordinated_attack_threshold = 5
        
        # Enhanced performance metrics
        self.cap_metrics = {
            'consistency_violations': 0,
            'availability_maintained': True,
            'partition_tolerance_active': False,
            'average_staleness': 0.0,
            'statistical_accuracy': 1.0,
            'recovery_time': 0.0,
            'temporal_attacks_blocked': 0,
            'partition_attacks_detected': 0,
            'staleness_jitter_effectiveness': 1.0
        }
        
        logger.info("Initialized SecureStatisticalCAPResolver with temporal attack prevention")
    
    def add_secure_node(self, node_id: str) -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        """Add node with cryptographic key generation for secure timestamping"""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        self.node_private_keys[node_id] = private_key
        self.node_public_keys[node_id] = public_key
        self.nodes.add(node_id)
        
        # Initialize secure vector clock
        initial_timestamp = CryptographicTimestamp(
            logical_time=0,
            wall_clock=time.time(),
            node_id=node_id
        )
        initial_timestamp.sign_timestamp(private_key)
        self.secure_vector_clocks[node_id] = initial_timestamp
        
        logger.info(f"Added secure node {node_id} with cryptographic timestamping")
        return private_key, public_key
    
    def detect_secure_network_partition(self, 
                                      connectivity_matrix: Dict[Tuple[str, str], bool],
                                      timestamp: float) -> NetworkPartitionState:
        """
        Enhanced partition detection with attack pattern recognition
        """
        # Standard partition detection
        partition_state = self._detect_basic_partitions(connectivity_matrix)
        
        # Security analysis: detect suspicious partition patterns
        partition_event = {
            'timestamp': timestamp,
            'state': partition_state,
            'affected_nodes': self._get_affected_nodes(connectivity_matrix)
        }
        self.partition_history.append(partition_event)
        
        # Analyze for coordinated timing attacks
        if self._detect_partition_attack_patterns():
            partition_state = NetworkPartitionState.ATTACK_SUSPECTED
            self.cap_metrics['partition_attacks_detected'] += 1
            logger.warning("Suspicious partition pattern detected - possible coordinated attack")
        
        self.current_partition_state = partition_state
        return partition_state
    
    def store_secure_statistical_data(self, 
                                    data: SecureStatisticalData,
                                    node_id: str) -> bool:
        """Store statistical data with cryptographic verification and jittered staleness"""
        # Verify cryptographic integrity
        if node_id not in self.node_public_keys:
            logger.error(f"Unknown node {node_id} attempting to store data")
            return False
        
        public_key = self.node_public_keys[node_id]
        if not data.verify_integrity(public_key):
            logger.error(f"Cryptographic verification failed for data {data.data_id}")
            self.cap_metrics['temporal_attacks_blocked'] += 1
            return False
        
        # Apply jittered staleness bound
        if self.randomize_staleness:
            min_bound, max_bound = self.dynamic_staleness_bounds[data.data_type]
            data.actual_staleness_bound = min_bound + random.random() * (max_bound - min_bound)
            logger.debug(f"Applied jittered staleness: {data.actual_staleness_bound:.2f}s for {data.data_type}")
        
        # Store with enhanced metadata
        self.statistical_data[data.data_id] = data
        return True
    
    async def resolve_statistical_cap_conflict(self, 
                                             data_requests: List[str],
                                             partition_state: NetworkPartitionState) -> Dict[str, Any]:
        """
        Resolve CAP conflicts with enhanced security during partitions
        """
        start_time = time.time()
        
        # Adaptive consistency requirements based on partition state and security
        if partition_state in [NetworkPartitionState.ATTACK_SUSPECTED, 
                             NetworkPartitionState.SEVERE_PARTITION]:
            # Enhanced security mode: require supermajority consensus
            consistency_threshold = 0.75  # 75% consensus required
            staleness_penalty = 0.8  # Tighter staleness bounds
        elif partition_state == NetworkPartitionState.MAJOR_PARTITION:
            consistency_threshold = 0.67  # 67% consensus required
            staleness_penalty = 0.9
        else:
            consistency_threshold = 0.51  # Simple majority
            staleness_penalty = 1.0
        
        # Collect available data with jittered staleness checking
        available_data = {}
        current_time = time.time()
        
        for data_id in data_requests:
            if data_id in self.statistical_data:
                data = self.statistical_data[data_id]
                
                # Check staleness with randomized bounds
                adjusted_staleness = data.actual_staleness_bound * staleness_penalty
                age = current_time - data.secure_timestamp.wall_clock
                
                if age <= adjusted_staleness:
                    available_data[data_id] = data
                else:
                    logger.debug(f"Data {data_id} is stale: {age:.2f}s > {adjusted_staleness:.2f}s")
        
        # Check if we have sufficient consensus
        total_nodes = len(self.nodes)
        available_nodes = len(set(data.source_node for data in available_data.values()))
        consensus_ratio = available_nodes / total_nodes if total_nodes > 0 else 0
        
        if consensus_ratio < consistency_threshold:
            # Insufficient consensus - apply jittered delay before retry
            jitter_delay = 0.1 + random.random() * 0.5  # 0.1-0.6 second jitter
            await asyncio.sleep(jitter_delay)
            
            return {
                'status': 'insufficient_consensus',
                'available_ratio': consensus_ratio,
                'required_ratio': consistency_threshold,
                'retry_after': jitter_delay
            }
        
        # Compute consensus result with security weighting
        consensus_result = await self._compute_secure_consensus(available_data, partition_state)
        
        # Calculate statistical accuracy impact
        accuracy_impact = min(1.0, consensus_ratio / consistency_threshold)
        
        resolution_time = time.time() - start_time
        self.cap_metrics['recovery_time'] = resolution_time
        self.cap_metrics['statistical_accuracy'] = accuracy_impact
        
        return {
            'status': 'resolved',
            'consensus_result': consensus_result,
            'accuracy_impact': accuracy_impact,
            'resolution_time': resolution_time,
            'security_level': consistency_threshold
        }
    
    async def _compute_secure_consensus(self, 
                                      available_data: Dict[str, SecureStatisticalData],
                                      partition_state: NetworkPartitionState) -> Dict[str, Any]:
        """Compute consensus with enhanced security weighting"""
        if not available_data:
            return {}
        
        # Weight data by timestamp freshness and cryptographic validity
        weighted_data = {}
        current_time = time.time()
        
        for data_id, data in available_data.items():
            # Freshness weight (newer data gets higher weight)
            age = current_time - data.secure_timestamp.wall_clock
            freshness_weight = max(0.1, 1.0 - (age / data.actual_staleness_bound))
            
            # Security weight (cryptographically verified data gets full weight)
            security_weight = 1.0 if data.content_signature else 0.5
            
            # Partition resistance weight
            partition_weight = 1.0
            if partition_state in [NetworkPartitionState.MAJOR_PARTITION, NetworkPartitionState.SEVERE_PARTITION]:
                partition_weight = 0.8 if data.partition_tolerant else 0.3
            
            total_weight = freshness_weight * security_weight * partition_weight
            weighted_data[data_id] = (data, total_weight)
        
        # Combine weighted statistical data
        if weighted_data:
            # Simplified consensus: weighted average of numerical values
            consensus_values = {}
            total_weight = sum(weight for _, weight in weighted_data.values())
            
            for data_id, (data, weight) in weighted_data.items():
                for key, value in data.content.items():
                    if isinstance(value, (int, float)):
                        if key not in consensus_values:
                            consensus_values[key] = 0.0
                        consensus_values[key] += value * (weight / total_weight)
            
            return consensus_values
        
        return {}
    
    def _detect_basic_partitions(self, connectivity_matrix: Dict[Tuple[str, str], bool]) -> NetworkPartitionState:
        """Basic partition detection using connected components"""
        # Build adjacency graph
        adjacency = defaultdict(set)
        for (node1, node2), connected in connectivity_matrix.items():
            if connected:
                adjacency[node1].add(node2)
                adjacency[node2].add(node1)
        
        # Find connected components
        visited = set()
        partitions = []
        
        for node in self.nodes:
            if node not in visited:
                partition_nodes = set()
                queue = deque([node])
                
                while queue:
                    current = queue.popleft()
                    if current not in visited:
                        visited.add(current)
                        partition_nodes.add(current)
                        queue.extend(adjacency[current] - visited)
                
                if partition_nodes:
                    partitions.append(partition_nodes)
        
        self.partitions = partitions
        
        # Classify partition severity
        if len(partitions) == 1:
            return NetworkPartitionState.FULLY_CONNECTED
        
        largest_partition_size = max(len(p) for p in partitions)
        partition_ratio = largest_partition_size / len(self.nodes)
        
        if partition_ratio > 0.8:
            return NetworkPartitionState.MINOR_PARTITION
        elif partition_ratio > 0.5:
            return NetworkPartitionState.MAJOR_PARTITION
        else:
            return NetworkPartitionState.SEVERE_PARTITION
    
    def _detect_partition_attack_patterns(self) -> bool:
        """Detect suspicious partition patterns that suggest coordinated attacks"""
        if len(self.partition_history) < 5:
            return False
        
        recent_events = list(self.partition_history)[-5:]
        
        # Pattern 1: Rapid partition state changes (potential timing attack)
        state_changes = 0
        for i in range(1, len(recent_events)):
            if recent_events[i]['state'] != recent_events[i-1]['state']:
                state_changes += 1
        
        if state_changes > 3:  # Too many rapid changes
            return True
        
        # Pattern 2: Periodic partition timing (potential coordinated attack)
        timestamps = [event['timestamp'] for event in recent_events]
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        if len(set(round(interval, 1) for interval in intervals)) == 1:  # Regular intervals
            return True
        
        # Pattern 3: Consistent node targeting (potential targeted attack)
        affected_nodes = set()
        for event in recent_events:
            affected_nodes.update(event['affected_nodes'])
        
        if len(affected_nodes) < 0.3 * len(self.nodes):  # Same nodes repeatedly affected
            return True
        
        return False
    
    def _get_affected_nodes(self, connectivity_matrix: Dict[Tuple[str, str], bool]) -> Set[str]:
        """Get nodes affected by current partition"""
        disconnected_nodes = set()
        
        for (node1, node2), connected in connectivity_matrix.items():
            if not connected:
                disconnected_nodes.add(node1)
                disconnected_nodes.add(node2)
        
        return disconnected_nodes
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status for CAP resolver"""
        return {
            'partition_state': self.current_partition_state.value,
            'staleness_randomization': self.randomize_staleness,
            'total_nodes': len(self.nodes),
            'active_partitions': len(self.partitions),
            'suspicious_patterns': self.suspicious_partition_patterns,
            'data_items_stored': len(self.statistical_data),
            'metrics': self.cap_metrics
        }

# Backwards compatibility
SecureStatisticalCAPResolver.__name__ = "StatisticalCAPResolver"

logger.info("Security-hardened statistical CAP resolver loaded with temporal attack prevention")