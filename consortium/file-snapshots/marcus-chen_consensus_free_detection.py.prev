#!/usr/bin/env python3
"""
Consensus-Free Distributed Detection Protocol
Dr. Marcus Chen - TCP Research Consortium

This implements a distributed detection system that can adapt network topology
and isolate compromised agents without requiring explicit consensus mechanisms.
The key insight: local behavioral observations can drive global network adaptation
through emergent consensus patterns.

Core Philosophy: "Networks should heal themselves faster than attackers can adapt"
"""

import asyncio
import time
import numpy as np
from typing import Dict, Set, List, Optional, Tuple, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import hashlib
import json

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """States a network node can be in"""
    HEALTHY = "healthy"
    SUSPICIOUS = "suspicious"
    QUARANTINED = "quarantined"
    ISOLATED = "isolated"
    RECOVERING = "recovering"


class TrustLevel(Enum):
    """Trust levels between nodes"""
    FULL_TRUST = 1.0
    HIGH_TRUST = 0.8
    MODERATE_TRUST = 0.6
    LOW_TRUST = 0.4
    DISTRUST = 0.2
    NO_TRUST = 0.0


@dataclass
class BehavioralSignal:
    """Behavioral signal observed from a node"""
    source_node: str
    target_node: str
    signal_type: str
    confidence: float
    evidence: Dict
    timestamp: float
    observation_window: int  # Number of interactions observed


@dataclass
class NetworkEdge:
    """Edge in the network topology with trust and routing information"""
    source: str
    target: str
    trust_level: float
    route_weight: float
    last_updated: float
    interaction_count: int = 0
    success_rate: float = 1.0
    
    def update_trust(self, new_trust: float, decay_factor: float = 0.9):
        """Update trust level with temporal decay"""
        self.trust_level = (self.trust_level * decay_factor) + (new_trust * (1 - decay_factor))
        self.last_updated = time.time()


@dataclass
class NodeProfile:
    """Profile of a network node's behavior and state"""
    node_id: str
    state: NodeState = NodeState.HEALTHY
    trust_score: float = 1.0
    behavioral_baseline: Dict = field(default_factory=dict)
    recent_signals: deque = field(default_factory=lambda: deque(maxlen=100))
    quarantine_history: List = field(default_factory=list)
    adaptation_count: int = 0
    
    def add_signal(self, signal: BehavioralSignal):
        """Add a new behavioral signal"""
        self.recent_signals.append(signal)
        
    def calculate_anomaly_score(self) -> float:
        """Calculate current anomaly score based on recent signals"""
        if not self.recent_signals:
            return 0.0
            
        recent_window = list(self.recent_signals)[-20:]  # Last 20 signals
        anomaly_scores = [1.0 - signal.confidence for signal in recent_window]
        return np.mean(anomaly_scores) if anomaly_scores else 0.0


class ConsensusFreeTopo:
    """
    Consensus-free network topology that adapts based on local observations.
    Nodes make independent routing decisions that collectively create emergent consensus.
    """
    
    def __init__(self, adaptation_threshold: float = 0.6, isolation_threshold: float = 0.8):
        self.nodes: Dict[str, NodeProfile] = {}
        self.edges: Dict[Tuple[str, str], NetworkEdge] = {}
        self.behavioral_signals: deque = deque(maxlen=10000)
        self.adaptation_threshold = adaptation_threshold
        self.isolation_threshold = isolation_threshold
        
        # Routing tables - maintained independently by each node's perspective
        self.routing_tables: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        
        # Network health metrics
        self.health_metrics = {
            'active_nodes': set(),
            'quarantined_nodes': set(),
            'adaptation_events': [],
            'network_efficiency': 1.0
        }
    
    def add_node(self, node_id: str) -> NodeProfile:
        """Add a new node to the network"""
        if node_id not in self.nodes:
            self.nodes[node_id] = NodeProfile(node_id=node_id)
            self.health_metrics['active_nodes'].add(node_id)
            self._initialize_routing_for_node(node_id)
            logger.info(f"Added node {node_id} to network")
        return self.nodes[node_id]
    
    def add_edge(self, source: str, target: str, initial_trust: float = 1.0):
        """Add an edge between two nodes"""
        edge_key = (source, target)
        if edge_key not in self.edges:
            self.edges[edge_key] = NetworkEdge(
                source=source,
                target=target,
                trust_level=initial_trust,
                route_weight=1.0 / initial_trust,  # Lower trust = higher routing cost
                last_updated=time.time()
            )
            self._update_routing_tables(source, target)
    
    def observe_behavior(self, source: str, target: str, 
                        assessment_accuracy: float, interaction_type: str) -> BehavioralSignal:
        """
        Observe behavioral interaction between nodes.
        This is where Elena's detection algorithms would feed in.
        """
        signal = BehavioralSignal(
            source_node=source,
            target_node=target,
            signal_type=interaction_type,
            confidence=assessment_accuracy,
            evidence={'accuracy': assessment_accuracy, 'type': interaction_type},
            timestamp=time.time(),
            observation_window=len(self.nodes[target].recent_signals) if target in self.nodes else 0
        )
        
        self.behavioral_signals.append(signal)
        
        if target in self.nodes:
            self.nodes[target].add_signal(signal)
        
        # Update edge trust based on behavioral observation
        edge_key = (source, target)
        if edge_key in self.edges:
            # Poor assessment accuracy reduces trust
            trust_adjustment = assessment_accuracy if assessment_accuracy > 0.5 else assessment_accuracy * 0.5
            self.edges[edge_key].update_trust(trust_adjustment)
        
        return signal
    
    async def adapt_topology(self) -> Dict[str, int]:
        """
        Core adaptive algorithm: analyze behavioral patterns and adapt network topology
        without requiring explicit consensus. Each node makes independent decisions
        that create emergent global behavior.
        """
        adaptation_events = {
            'quarantined': 0,
            'isolated': 0,
            'routes_updated': 0,
            'trust_adjustments': 0
        }
        
        # Analyze each node for adaptation needs
        for node_id, profile in self.nodes.items():
            if profile.state == NodeState.ISOLATED:
                continue
                
            anomaly_score = profile.calculate_anomaly_score()
            
            # Local decision making - no coordination required
            if anomaly_score >= self.isolation_threshold:
                await self._isolate_node(node_id, anomaly_score)
                adaptation_events['isolated'] += 1
                
            elif anomaly_score >= self.adaptation_threshold:
                await self._quarantine_node(node_id, anomaly_score)
                adaptation_events['quarantined'] += 1
        
        # Update routing tables based on current trust levels
        routes_updated = await self._adapt_routing_tables()
        adaptation_events['routes_updated'] = routes_updated
        
        # Update network health metrics
        self._update_health_metrics()
        
        logger.info(f"Topology adaptation completed: {adaptation_events}")
        return adaptation_events
    
    async def _isolate_node(self, node_id: str, anomaly_score: float):
        """Isolate a highly suspicious node from the network"""
        if node_id in self.nodes:
            profile = self.nodes[node_id]
            profile.state = NodeState.ISOLATED
            profile.trust_score = 0.0
            
            # Remove from active routing
            self.health_metrics['active_nodes'].discard(node_id)
            self.health_metrics['quarantined_nodes'].add(node_id)
            
            # Update all edges involving this node
            for edge_key, edge in self.edges.items():
                if edge.source == node_id or edge.target == node_id:
                    edge.trust_level = 0.0
                    edge.route_weight = float('inf')  # Infinite cost = no routing
            
            logger.warning(f"Node {node_id} ISOLATED (anomaly score: {anomaly_score:.3f})")
    
    async def _quarantine_node(self, node_id: str, anomaly_score: float):
        """Move node to quarantine state with limited network access"""
        if node_id in self.nodes:
            profile = self.nodes[node_id]
            profile.state = NodeState.QUARANTINED
            profile.trust_score = 0.3  # Limited trust
            profile.adaptation_count += 1
            
            # Reduce trust on all edges involving this node
            for edge_key, edge in self.edges.items():
                if edge.source == node_id or edge.target == node_id:
                    edge.trust_level = min(edge.trust_level, 0.3)
                    edge.route_weight = 1.0 / edge.trust_level
            
            profile.quarantine_history.append({
                'timestamp': time.time(),
                'anomaly_score': anomaly_score,
                'reason': 'behavioral_deviation'
            })
            
            logger.warning(f"Node {node_id} QUARANTINED (anomaly score: {anomaly_score:.3f})")
    
    async def _adapt_routing_tables(self) -> int:
        """
        Adapt routing tables to bypass low-trust nodes.
        This creates semantic routing that naturally avoids compromised nodes.
        """
        routes_updated = 0
        
        for source_node in self.nodes:
            if self.nodes[source_node].state == NodeState.ISOLATED:
                continue
                
            # Recalculate optimal paths avoiding low-trust nodes
            new_routes = self._calculate_trust_weighted_paths(source_node)
            
            if source_node not in self.routing_tables:
                self.routing_tables[source_node] = {}
                
            # Update routes that have changed
            for target, path in new_routes.items():
                old_path = self.routing_tables[source_node].get(target, [])
                if path != old_path:
                    self.routing_tables[source_node][target] = path
                    routes_updated += 1
        
        return routes_updated
    
    def _calculate_trust_weighted_paths(self, source: str) -> Dict[str, List[str]]:
        """
        Calculate shortest paths weighted by trust levels.
        Uses Dijkstra's algorithm with trust-based edge weights.
        """
        paths = {}
        distances = {node: float('inf') for node in self.nodes}
        distances[source] = 0
        previous = {}
        unvisited = set(self.nodes.keys())
        
        while unvisited:
            # Find node with minimum distance
            current = min(unvisited, key=lambda x: distances[x])
            unvisited.remove(current)
            
            if distances[current] == float('inf'):
                break
                
            # Check all neighbors
            for edge_key, edge in self.edges.items():
                if edge.source == current and edge.target in unvisited:
                    neighbor = edge.target
                    
                    # Skip if neighbor is isolated
                    if self.nodes[neighbor].state == NodeState.ISOLATED:
                        continue
                        
                    distance = distances[current] + edge.route_weight
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current
        
        # Reconstruct paths
        for target in self.nodes:
            if target != source and target in previous:
                path = []
                current = target
                while current != source:
                    path.insert(0, current)
                    current = previous.get(current)
                    if current is None:
                        break
                if current == source:
                    path.insert(0, source)
                    paths[target] = path
        
        return paths
    
    def _initialize_routing_for_node(self, node_id: str):
        """Initialize routing table for a new node"""
        if node_id not in self.routing_tables:
            self.routing_tables[node_id] = {}
    
    def _update_routing_tables(self, source: str, target: str):
        """Update routing tables when new edge is added"""
        # This would trigger a routing table recalculation
        # For now, we'll do this during the main adaptation cycle
        pass
    
    def _update_health_metrics(self):
        """Update overall network health metrics"""
        total_nodes = len(self.nodes)
        active_nodes = len([n for n in self.nodes.values() if n.state not in [NodeState.ISOLATED]])
        
        self.health_metrics['network_efficiency'] = active_nodes / total_nodes if total_nodes > 0 else 0.0
        
        # Record adaptation event
        self.health_metrics['adaptation_events'].append({
            'timestamp': time.time(),
            'active_nodes': active_nodes,
            'total_nodes': total_nodes,
            'efficiency': self.health_metrics['network_efficiency']
        })
    
    def get_route(self, source: str, target: str) -> Optional[List[str]]:
        """Get the current optimal route between two nodes"""
        return self.routing_tables.get(source, {}).get(target)
    
    def get_network_health(self) -> Dict:
        """Get current network health status"""
        healthy_nodes = len([n for n in self.nodes.values() if n.state == NodeState.HEALTHY])
        quarantined_nodes = len([n for n in self.nodes.values() if n.state == NodeState.QUARANTINED])
        isolated_nodes = len([n for n in self.nodes.values() if n.state == NodeState.ISOLATED])
        
        return {
            'total_nodes': len(self.nodes),
            'healthy_nodes': healthy_nodes,
            'quarantined_nodes': quarantined_nodes,
            'isolated_nodes': isolated_nodes,
            'network_efficiency': self.health_metrics['network_efficiency'],
            'adaptation_events_count': len(self.health_metrics['adaptation_events'])
        }


class DistributedDetectionOrchestrator:
    """
    Orchestrates multiple consensus-free networks and coordinates with Elena's
    behavioral detection algorithms.
    """
    
    def __init__(self, networks: Optional[Dict[str, ConsensusFreeTopo]] = None):
        self.networks = networks or {}
        self.cross_network_signals = deque(maxlen=1000)
        
    def add_network(self, network_id: str, network: ConsensusFreeTopo):
        """Add a network to the orchestrator"""
        self.networks[network_id] = network
        logger.info(f"Added network {network_id} to orchestrator")
    
    async def orchestrate_detection(self, elena_behavioral_data: List[Dict]) -> Dict:
        """
        Coordinate detection across all networks using Elena's behavioral analysis.
        This is the integration point with Elena's statistical models.
        """
        results = {
            'networks_adapted': 0,
            'total_isolations': 0,
            'total_quarantines': 0,
            'cross_network_patterns': []
        }
        
        # Process behavioral data from Elena's algorithms
        for behavior_data in elena_behavioral_data:
            network_id = behavior_data.get('network_id', 'default')
            source_node = behavior_data.get('source_node')
            target_node = behavior_data.get('target_node')
            accuracy_score = behavior_data.get('assessment_accuracy', 0.5)
            interaction_type = behavior_data.get('interaction_type', 'command_assessment')
            
            if network_id in self.networks:
                # Feed behavioral observation into the appropriate network
                signal = self.networks[network_id].observe_behavior(
                    source_node, target_node, accuracy_score, interaction_type
                )
                
                self.cross_network_signals.append({
                    'network_id': network_id,
                    'signal': signal,
                    'timestamp': time.time()
                })
        
        # Adapt all networks
        for network_id, network in self.networks.items():
            adaptation_result = await network.adapt_topology()
            
            if any(adaptation_result.values()):
                results['networks_adapted'] += 1
                results['total_isolations'] += adaptation_result['isolated']
                results['total_quarantines'] += adaptation_result['quarantined']
        
        return results
    
    def get_global_health(self) -> Dict:
        """Get health status across all networks"""
        global_health = {
            'total_networks': len(self.networks),
            'network_health': {},
            'overall_efficiency': 0.0
        }
        
        total_efficiency = 0.0
        for network_id, network in self.networks.items():
            health = network.get_network_health()
            global_health['network_health'][network_id] = health
            total_efficiency += health['network_efficiency']
        
        global_health['overall_efficiency'] = total_efficiency / len(self.networks) if self.networks else 0.0
        
        return global_health


# Integration point for Elena's behavioral detection
async def integrate_with_elena_detection(orchestrator: DistributedDetectionOrchestrator,
                                      elena_assessment_stream: AsyncIterator[Dict]):
    """
    Integration function that connects Elena's behavioral detection
    with the distributed network adaptation system.
    """
    behavioral_batch = []
    
    async for assessment in elena_assessment_stream:
        behavioral_batch.append(assessment)
        
        # Process in batches for efficiency
        if len(behavioral_batch) >= 10:
            await orchestrator.orchestrate_detection(behavioral_batch)
            behavioral_batch.clear()
    
    # Process remaining assessments
    if behavioral_batch:
        await orchestrator.orchestrate_detection(behavioral_batch)


if __name__ == "__main__":
    # Example usage demonstrating the consensus-free detection protocol
    async def demo_consensus_free_detection():
        # Create a network topology
        network = ConsensusFreeTopo(adaptation_threshold=0.6, isolation_threshold=0.8)
        
        # Add nodes (representing TCP agents)
        nodes = ['agent_001', 'agent_002', 'agent_003', 'agent_004', 'agent_005']
        for node in nodes:
            network.add_node(node)
        
        # Add edges (communication paths)
        for i, node in enumerate(nodes):
            for other_node in nodes[i+1:]:
                network.add_edge(node, other_node)
        
        # Simulate behavioral observations (from Elena's detection)
        compromised_node = 'agent_003'
        
        # Normal behavior for most nodes
        for _ in range(20):
            source = np.random.choice([n for n in nodes if n != compromised_node])
            target = np.random.choice([n for n in nodes if n != source])
            accuracy = np.random.normal(0.85, 0.1)  # Good performance
            network.observe_behavior(source, target, accuracy, 'normal_assessment')
        
        # Compromised behavior for one node
        for _ in range(15):
            source = np.random.choice(nodes)
            accuracy = np.random.normal(0.3, 0.1)  # Poor performance indicating compromise
            network.observe_behavior(source, compromised_node, accuracy, 'compromised_assessment')
        
        # Adapt network topology
        adaptation_result = await network.adapt_topology()
        
        print("=== Consensus-Free Detection Results ===")
        print(f"Adaptation events: {adaptation_result}")
        print(f"Network health: {network.get_network_health()}")
        
        # Show routing adaptation
        for source in nodes[:2]:  # Show routing for first 2 nodes
            for target in nodes:
                if source != target:
                    route = network.get_route(source, target)
                    print(f"Route {source} -> {target}: {route}")
    
    # Run the demo
    asyncio.run(demo_consensus_free_detection())