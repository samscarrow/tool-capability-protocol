#!/usr/bin/env python3
"""
Network Topology Evolution Algorithms
Dr. Marcus Chen - TCP Research Consortium

This implements algorithms that evolve network topology in real-time to optimize
for security, performance, and resilience. The network literally rewires itself
to route around threats and create stronger defensive patterns.

Core Philosophy: "Networks that evolve survive - static topologies are vulnerable topologies"
"""

import asyncio
import time
import numpy as np
from typing import Dict, Set, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from collections import defaultdict, deque
import networkx as nx
import random
import math
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EvolutionStrategy(Enum):
    """Strategies for network topology evolution"""
    GENETIC_ALGORITHM = "genetic"
    GRADIENT_DESCENT = "gradient"
    SWARM_OPTIMIZATION = "swarm"
    REINFORCEMENT_LEARNING = "rl"
    HYBRID_ADAPTIVE = "hybrid"


class TopologyMetric(Enum):
    """Metrics for evaluating network topologies"""
    SECURITY_RESILIENCE = "security"
    COMMUNICATION_EFFICIENCY = "efficiency"
    FAULT_TOLERANCE = "fault_tolerance"
    ISOLATION_CAPABILITY = "isolation"
    ADAPTATION_SPEED = "adaptation_speed"


@dataclass
class NetworkNode:
    """Node in the evolving network topology"""
    node_id: str
    trust_level: float = 1.0
    processing_capacity: float = 1.0
    communication_latency: float = 0.1
    security_level: float = 1.0
    connection_preferences: Set[str] = field(default_factory=set)
    quarantine_status: bool = False
    
    def fitness_score(self) -> float:
        """Calculate fitness score for evolution algorithms"""
        base_fitness = (self.trust_level * 0.4 + 
                       self.security_level * 0.3 + 
                       self.processing_capacity * 0.2 + 
                       (1.0 - self.communication_latency) * 0.1)
        
        # Penalty for quarantined nodes
        if self.quarantine_status:
            base_fitness *= 0.3
            
        return base_fitness


@dataclass
class NetworkEdge:
    """Edge in the evolving network topology"""
    source: str
    target: str
    weight: float = 1.0
    trust_level: float = 1.0
    bandwidth: float = 1.0
    latency: float = 0.1
    reliability: float = 1.0
    last_used: float = field(default_factory=time.time)
    
    def edge_fitness(self) -> float:
        """Calculate edge fitness for evolution"""
        recency_factor = max(0.1, 1.0 - (time.time() - self.last_used) / 3600)  # Decay over 1 hour
        return (self.trust_level * 0.3 + 
                self.reliability * 0.3 + 
                self.bandwidth * 0.2 + 
                (1.0 - self.latency) * 0.1 + 
                recency_factor * 0.1)


@dataclass
class TopologyGenome:
    """Genetic representation of network topology"""
    node_connections: Dict[str, Set[str]]
    edge_weights: Dict[Tuple[str, str], float]
    fitness_score: float = 0.0
    generation: int = 0
    
    def mutate(self, mutation_rate: float = 0.1):
        """Mutate the topology genome"""
        nodes = list(self.node_connections.keys())
        
        for node in nodes:
            if random.random() < mutation_rate:
                # Add or remove a connection
                if random.random() < 0.5 and len(nodes) > 1:
                    # Add connection
                    potential_targets = [n for n in nodes if n != node and n not in self.node_connections[node]]
                    if potential_targets:
                        new_target = random.choice(potential_targets)
                        self.node_connections[node].add(new_target)
                        self.edge_weights[(node, new_target)] = random.uniform(0.1, 1.0)
                else:
                    # Remove connection
                    if self.node_connections[node]:
                        target_to_remove = random.choice(list(self.node_connections[node]))
                        self.node_connections[node].discard(target_to_remove)
                        self.edge_weights.pop((node, target_to_remove), None)
        
        # Mutate edge weights
        for edge_key in list(self.edge_weights.keys()):
            if random.random() < mutation_rate:
                current_weight = self.edge_weights[edge_key]
                mutation_delta = random.uniform(-0.2, 0.2)
                new_weight = max(0.1, min(1.0, current_weight + mutation_delta))
                self.edge_weights[edge_key] = new_weight


class EvolvingNetworkTopology:
    """
    Network topology that evolves using genetic algorithms and other optimization techniques
    to maximize security, efficiency, and resilience.
    """
    
    def __init__(self, evolution_strategy: EvolutionStrategy = EvolutionStrategy.HYBRID_ADAPTIVE):
        self.nodes: Dict[str, NetworkNode] = {}
        self.edges: Dict[Tuple[str, str], NetworkEdge] = {}
        self.evolution_strategy = evolution_strategy
        
        # Evolution parameters
        self.population_size = 20
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elitism_ratio = 0.2
        
        # Current topology genome
        self.current_genome: Optional[TopologyGenome] = None
        self.evolution_history: deque = deque(maxlen=100)
        
        # Fitness evaluation weights
        self.fitness_weights = {
            TopologyMetric.SECURITY_RESILIENCE: 0.3,
            TopologyMetric.COMMUNICATION_EFFICIENCY: 0.25,
            TopologyMetric.FAULT_TOLERANCE: 0.25,
            TopologyMetric.ISOLATION_CAPABILITY: 0.15,
            TopologyMetric.ADAPTATION_SPEED: 0.05
        }
        
        # NetworkX graph for advanced analysis
        self.graph = nx.Graph()
    
    def add_node(self, node_id: str, **node_properties) -> NetworkNode:
        """Add a node to the evolving topology"""
        node = NetworkNode(node_id=node_id, **node_properties)
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node_properties)
        
        # Update current genome if it exists
        if self.current_genome:
            self.current_genome.node_connections[node_id] = set()
        
        logger.info(f"Added node {node_id} to evolving topology")
        return node
    
    def add_edge(self, source: str, target: str, **edge_properties) -> NetworkEdge:
        """Add an edge to the evolving topology"""
        edge = NetworkEdge(source=source, target=target, **edge_properties)
        edge_key = (source, target)
        self.edges[edge_key] = edge
        
        # Add to NetworkX graph
        self.graph.add_edge(source, target, **edge_properties)
        
        # Update current genome
        if self.current_genome:
            if source not in self.current_genome.node_connections:
                self.current_genome.node_connections[source] = set()
            if target not in self.current_genome.node_connections:
                self.current_genome.node_connections[target] = set()
            
            self.current_genome.node_connections[source].add(target)
            self.current_genome.edge_weights[edge_key] = edge.weight
        
        logger.info(f"Added edge {source} -> {target} to evolving topology")
        return edge
    
    async def evolve_topology(self, threat_context: Dict[str, Any], 
                            target_metrics: Dict[TopologyMetric, float]) -> Dict[str, Any]:
        """
        Evolve the network topology to optimize for given metrics and respond to threats.
        This is the main evolution engine.
        """
        evolution_results = {
            'generation': 0,
            'fitness_improvement': 0.0,
            'topology_changes': [],
            'evolution_strategy': self.evolution_strategy.value,
            'convergence_achieved': False
        }
        
        # Initialize genome if not exists
        if not self.current_genome:
            self.current_genome = self._create_initial_genome()
        
        initial_fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
        
        if self.evolution_strategy == EvolutionStrategy.GENETIC_ALGORITHM:
            evolution_results = await self._genetic_evolution(threat_context, target_metrics)
        elif self.evolution_strategy == EvolutionStrategy.GRADIENT_DESCENT:
            evolution_results = await self._gradient_evolution(threat_context, target_metrics)
        elif self.evolution_strategy == EvolutionStrategy.SWARM_OPTIMIZATION:
            evolution_results = await self._swarm_evolution(threat_context, target_metrics)
        elif self.evolution_strategy == EvolutionStrategy.HYBRID_ADAPTIVE:
            evolution_results = await self._hybrid_evolution(threat_context, target_metrics)
        
        # Apply the best evolved topology
        await self._apply_evolved_topology(self.current_genome)
        
        final_fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
        evolution_results['fitness_improvement'] = final_fitness - initial_fitness
        
        # Record evolution history
        self.evolution_history.append({
            'timestamp': time.time(),
            'initial_fitness': initial_fitness,
            'final_fitness': final_fitness,
            'improvement': evolution_results['fitness_improvement'],
            'strategy': self.evolution_strategy.value
        })
        
        logger.info(f"Topology evolution completed: {evolution_results['fitness_improvement']:.3f} improvement")
        return evolution_results
    
    async def _genetic_evolution(self, threat_context: Dict, target_metrics: Dict) -> Dict[str, Any]:
        """Genetic algorithm for topology evolution"""
        results = {'generation': 0, 'topology_changes': [], 'convergence_achieved': False}
        
        # Create initial population
        population = [self.current_genome]
        for _ in range(self.population_size - 1):
            genome = self._create_mutated_genome(self.current_genome)
            population.append(genome)
        
        best_fitness = 0.0
        stagnation_count = 0
        max_generations = 50
        
        for generation in range(max_generations):
            # Evaluate fitness for all genomes
            fitness_scores = []
            for genome in population:
                fitness = await self._evaluate_topology_fitness(genome, target_metrics)
                genome.fitness_score = fitness
                fitness_scores.append(fitness)
            
            # Check for improvement
            current_best = max(fitness_scores)
            if current_best > best_fitness:
                best_fitness = current_best
                stagnation_count = 0
            else:
                stagnation_count += 1
            
            # Check convergence
            if stagnation_count >= 10:  # No improvement for 10 generations
                results['convergence_achieved'] = True
                break
            
            # Selection, crossover, and mutation
            population = await self._genetic_selection_crossover_mutation(population, threat_context)
            results['generation'] = generation + 1
        
        # Select best genome
        population.sort(key=lambda g: g.fitness_score, reverse=True)
        self.current_genome = population[0]
        
        return results
    
    async def _gradient_evolution(self, threat_context: Dict, target_metrics: Dict) -> Dict[str, Any]:
        """Gradient-based topology optimization"""
        results = {'generation': 0, 'topology_changes': [], 'convergence_achieved': False}
        
        learning_rate = 0.01
        max_iterations = 100
        
        for iteration in range(max_iterations):
            # Calculate gradient by testing small changes
            current_fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
            
            # Test edge weight modifications
            improvements = []
            for edge_key, current_weight in self.current_genome.edge_weights.items():
                # Test small increase
                self.current_genome.edge_weights[edge_key] = min(1.0, current_weight + learning_rate)
                increased_fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
                
                # Test small decrease
                self.current_genome.edge_weights[edge_key] = max(0.1, current_weight - learning_rate)
                decreased_fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
                
                # Calculate gradient
                gradient = (increased_fitness - decreased_fitness) / (2 * learning_rate)
                improvements.append((edge_key, gradient, current_weight))
                
                # Restore original weight
                self.current_genome.edge_weights[edge_key] = current_weight
            
            # Apply gradients
            total_improvement = 0.0
            for edge_key, gradient, current_weight in improvements:
                new_weight = current_weight + learning_rate * gradient
                new_weight = max(0.1, min(1.0, new_weight))
                self.current_genome.edge_weights[edge_key] = new_weight
                total_improvement += abs(gradient)
            
            # Check convergence
            if total_improvement < 0.001:
                results['convergence_achieved'] = True
                break
            
            results['generation'] = iteration + 1
        
        return results
    
    async def _hybrid_evolution(self, threat_context: Dict, target_metrics: Dict) -> Dict[str, Any]:
        """Hybrid evolution combining multiple strategies"""
        results = {'generation': 0, 'topology_changes': [], 'convergence_achieved': False}
        
        # Start with genetic algorithm for exploration
        genetic_results = await self._genetic_evolution(threat_context, target_metrics)
        results['generation'] += genetic_results['generation']
        
        # Refine with gradient descent for exploitation
        gradient_results = await self._gradient_evolution(threat_context, target_metrics)
        results['generation'] += gradient_results['generation']
        
        # Apply swarm optimization for final tuning
        swarm_results = await self._swarm_evolution(threat_context, target_metrics)
        results['generation'] += swarm_results['generation']
        
        results['convergence_achieved'] = any([
            genetic_results.get('convergence_achieved', False),
            gradient_results.get('convergence_achieved', False),
            swarm_results.get('convergence_achieved', False)
        ])
        
        return results
    
    async def _swarm_evolution(self, threat_context: Dict, target_metrics: Dict) -> Dict[str, Any]:
        """Particle swarm optimization for topology evolution"""
        results = {'generation': 0, 'topology_changes': [], 'convergence_achieved': False}
        
        # Simplified swarm optimization for edge weights
        swarm_size = 10
        max_iterations = 30
        
        # Initialize particles (each particle represents edge weight configuration)
        particles = []
        velocities = []
        personal_best = []
        
        for _ in range(swarm_size):
            # Create particle as copy of current genome with small variations
            particle = {}
            velocity = {}
            for edge_key, weight in self.current_genome.edge_weights.items():
                particle[edge_key] = weight + random.uniform(-0.1, 0.1)
                particle[edge_key] = max(0.1, min(1.0, particle[edge_key]))
                velocity[edge_key] = random.uniform(-0.05, 0.05)
            
            particles.append(particle)
            velocities.append(velocity)
            personal_best.append(particle.copy())
        
        global_best = personal_best[0].copy()
        global_best_fitness = 0.0
        
        for iteration in range(max_iterations):
            # Evaluate particles
            for i, particle in enumerate(particles):
                # Temporarily apply particle weights
                original_weights = self.current_genome.edge_weights.copy()
                self.current_genome.edge_weights = particle
                
                fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
                
                # Update personal best
                if fitness > await self._get_particle_fitness(personal_best[i], target_metrics):
                    personal_best[i] = particle.copy()
                
                # Update global best
                if fitness > global_best_fitness:
                    global_best = particle.copy()
                    global_best_fitness = fitness
                
                # Restore original weights
                self.current_genome.edge_weights = original_weights
            
            # Update velocities and positions
            for i in range(swarm_size):
                for edge_key in velocities[i]:
                    # PSO velocity update
                    inertia = 0.7
                    cognitive = 1.5
                    social = 1.5
                    
                    r1, r2 = random.random(), random.random()
                    
                    velocities[i][edge_key] = (inertia * velocities[i][edge_key] + 
                                             cognitive * r1 * (personal_best[i][edge_key] - particles[i][edge_key]) +
                                             social * r2 * (global_best[edge_key] - particles[i][edge_key]))
                    
                    # Update position
                    particles[i][edge_key] += velocities[i][edge_key]
                    particles[i][edge_key] = max(0.1, min(1.0, particles[i][edge_key]))
            
            results['generation'] = iteration + 1
        
        # Apply best solution
        self.current_genome.edge_weights = global_best
        
        return results
    
    async def _get_particle_fitness(self, particle_weights: Dict, target_metrics: Dict) -> float:
        """Get fitness for a particle configuration"""
        original_weights = self.current_genome.edge_weights.copy()
        self.current_genome.edge_weights = particle_weights
        fitness = await self._evaluate_topology_fitness(self.current_genome, target_metrics)
        self.current_genome.edge_weights = original_weights
        return fitness
    
    def _create_initial_genome(self) -> TopologyGenome:
        """Create initial topology genome from current network state"""
        node_connections = defaultdict(set)
        edge_weights = {}
        
        for edge_key, edge in self.edges.items():
            source, target = edge_key
            node_connections[source].add(target)
            edge_weights[edge_key] = edge.weight
        
        # Ensure all nodes are represented
        for node_id in self.nodes:
            if node_id not in node_connections:
                node_connections[node_id] = set()
        
        return TopologyGenome(
            node_connections=dict(node_connections),
            edge_weights=edge_weights,
            generation=0
        )
    
    def _create_mutated_genome(self, parent_genome: TopologyGenome) -> TopologyGenome:
        """Create a mutated copy of a genome"""
        new_genome = TopologyGenome(
            node_connections={k: v.copy() for k, v in parent_genome.node_connections.items()},
            edge_weights=parent_genome.edge_weights.copy(),
            generation=parent_genome.generation + 1
        )
        new_genome.mutate(self.mutation_rate)
        return new_genome
    
    async def _genetic_selection_crossover_mutation(self, population: List[TopologyGenome], 
                                                  threat_context: Dict) -> List[TopologyGenome]:
        """Perform selection, crossover, and mutation for genetic algorithm"""
        # Sort by fitness
        population.sort(key=lambda g: g.fitness_score, reverse=True)
        
        # Elitism - keep best individuals
        elite_count = int(self.population_size * self.elitism_ratio)
        new_population = population[:elite_count]
        
        # Generate offspring through crossover and mutation
        while len(new_population) < self.population_size:
            if random.random() < self.crossover_rate and len(population) >= 2:
                # Crossover
                parent1 = self._tournament_selection(population[:len(population)//2])
                parent2 = self._tournament_selection(population[:len(population)//2])
                offspring = self._crossover_genomes(parent1, parent2)
            else:
                # Mutation only
                parent = self._tournament_selection(population[:len(population)//2])
                offspring = self._create_mutated_genome(parent)
            
            new_population.append(offspring)
        
        return new_population
    
    def _tournament_selection(self, candidates: List[TopologyGenome], tournament_size: int = 3) -> TopologyGenome:
        """Tournament selection for genetic algorithm"""
        tournament = random.sample(candidates, min(tournament_size, len(candidates)))
        return max(tournament, key=lambda g: g.fitness_score)
    
    def _crossover_genomes(self, parent1: TopologyGenome, parent2: TopologyGenome) -> TopologyGenome:
        """Crossover two genomes to create offspring"""
        offspring = TopologyGenome(
            node_connections={},
            edge_weights={},
            generation=max(parent1.generation, parent2.generation) + 1
        )
        
        # Crossover node connections
        all_nodes = set(parent1.node_connections.keys()) | set(parent2.node_connections.keys())
        for node in all_nodes:
            connections1 = parent1.node_connections.get(node, set())
            connections2 = parent2.node_connections.get(node, set())
            
            # Random combination of connections
            if random.random() < 0.5:
                offspring.node_connections[node] = connections1.copy()
            else:
                offspring.node_connections[node] = connections2.copy()
            
            # Sometimes add connections from both parents
            if random.random() < 0.3:
                offspring.node_connections[node] |= connections2
        
        # Crossover edge weights
        all_edges = set(parent1.edge_weights.keys()) | set(parent2.edge_weights.keys())
        for edge in all_edges:
            weight1 = parent1.edge_weights.get(edge, 0.5)
            weight2 = parent2.edge_weights.get(edge, 0.5)
            
            # Blend crossover
            alpha = random.random()
            offspring.edge_weights[edge] = alpha * weight1 + (1 - alpha) * weight2
        
        return offspring
    
    async def _evaluate_topology_fitness(self, genome: TopologyGenome, 
                                       target_metrics: Dict[TopologyMetric, float]) -> float:
        """Evaluate the fitness of a topology genome"""
        fitness_components = {}
        
        # Security resilience - based on network connectivity and trust distribution
        security_score = await self._calculate_security_resilience(genome)
        fitness_components[TopologyMetric.SECURITY_RESILIENCE] = security_score
        
        # Communication efficiency - based on path lengths and bandwidth
        efficiency_score = await self._calculate_communication_efficiency(genome)
        fitness_components[TopologyMetric.COMMUNICATION_EFFICIENCY] = efficiency_score
        
        # Fault tolerance - based on network redundancy
        fault_tolerance_score = await self._calculate_fault_tolerance(genome)
        fitness_components[TopologyMetric.FAULT_TOLERANCE] = fault_tolerance_score
        
        # Isolation capability - ability to isolate compromised nodes
        isolation_score = await self._calculate_isolation_capability(genome)
        fitness_components[TopologyMetric.ISOLATION_CAPABILITY] = isolation_score
        
        # Adaptation speed - how quickly topology can change
        adaptation_score = await self._calculate_adaptation_speed(genome)
        fitness_components[TopologyMetric.ADAPTATION_SPEED] = adaptation_score
        
        # Calculate weighted fitness
        total_fitness = 0.0
        for metric, weight in self.fitness_weights.items():
            component_score = fitness_components.get(metric, 0.5)
            target_score = target_metrics.get(metric, 0.5)
            
            # Fitness penalty for deviating from target
            deviation_penalty = abs(component_score - target_score)
            adjusted_score = component_score * (1.0 - deviation_penalty)
            
            total_fitness += weight * adjusted_score
        
        return total_fitness
    
    async def _calculate_security_resilience(self, genome: TopologyGenome) -> float:
        """Calculate security resilience score for the topology"""
        # Create temporary graph for analysis
        temp_graph = nx.Graph()
        
        for node in genome.node_connections:
            temp_graph.add_node(node)
        
        for node, connections in genome.node_connections.items():
            for target in connections:
                weight = genome.edge_weights.get((node, target), 0.5)
                temp_graph.add_edge(node, target, weight=weight)
        
        if len(temp_graph.nodes) == 0:
            return 0.0
        
        # Analyze network properties
        try:
            # Average clustering coefficient (higher is better for security)
            clustering = nx.average_clustering(temp_graph)
            
            # Network density (moderate density is optimal)
            density = nx.density(temp_graph)
            optimal_density = 0.3  # Not too sparse, not too dense
            density_score = 1.0 - abs(density - optimal_density)
            
            # Trust-weighted connectivity
            trust_weighted_score = 0.0
            edge_count = 0
            for edge in temp_graph.edges():
                edge_key = edge if edge in genome.edge_weights else (edge[1], edge[0])
                weight = genome.edge_weights.get(edge_key, 0.5)
                trust_weighted_score += weight
                edge_count += 1
            
            avg_trust = trust_weighted_score / edge_count if edge_count > 0 else 0.5
            
            # Combine components
            security_score = 0.4 * clustering + 0.3 * density_score + 0.3 * avg_trust
            
        except:
            security_score = 0.1  # Low score for invalid topologies
        
        return max(0.0, min(1.0, security_score))
    
    async def _calculate_communication_efficiency(self, genome: TopologyGenome) -> float:
        """Calculate communication efficiency score"""
        # Create temporary graph
        temp_graph = nx.Graph()
        
        for node in genome.node_connections:
            temp_graph.add_node(node)
        
        for node, connections in genome.node_connections.items():
            for target in connections:
                weight = 1.0 / genome.edge_weights.get((node, target), 0.5)  # Inverse weight for distance
                temp_graph.add_edge(node, target, weight=weight)
        
        if len(temp_graph.nodes) < 2:
            return 0.0
        
        try:
            # Average shortest path length (lower is better)
            if nx.is_connected(temp_graph):
                avg_path_length = nx.average_shortest_path_length(temp_graph, weight='weight')
                # Normalize (assuming max reasonable path length is 10)
                path_efficiency = max(0.0, 1.0 - avg_path_length / 10.0)
            else:
                path_efficiency = 0.1  # Low efficiency for disconnected graph
            
            # Bandwidth utilization (sum of edge weights)
            total_bandwidth = sum(genome.edge_weights.values())
            max_possible_bandwidth = len(genome.node_connections) * len(genome.node_connections)
            bandwidth_efficiency = min(1.0, total_bandwidth / max_possible_bandwidth) if max_possible_bandwidth > 0 else 0.0
            
            # Combine components
            efficiency_score = 0.6 * path_efficiency + 0.4 * bandwidth_efficiency
            
        except:
            efficiency_score = 0.1
        
        return max(0.0, min(1.0, efficiency_score))
    
    async def _calculate_fault_tolerance(self, genome: TopologyGenome) -> float:
        """Calculate fault tolerance score"""
        # Create temporary graph
        temp_graph = nx.Graph()
        
        for node in genome.node_connections:
            temp_graph.add_node(node)
        
        for node, connections in genome.node_connections.items():
            for target in connections:
                temp_graph.add_edge(node, target)
        
        if len(temp_graph.nodes) < 2:
            return 0.0
        
        try:
            # Node connectivity (minimum number of nodes to disconnect graph)
            node_connectivity = nx.node_connectivity(temp_graph)
            max_connectivity = len(temp_graph.nodes) - 1
            connectivity_score = node_connectivity / max_connectivity if max_connectivity > 0 else 0.0
            
            # Edge connectivity
            edge_connectivity = nx.edge_connectivity(temp_graph)
            max_edge_connectivity = len(temp_graph.nodes) * (len(temp_graph.nodes) - 1) // 2
            edge_connectivity_score = edge_connectivity / max_edge_connectivity if max_edge_connectivity > 0 else 0.0
            
            # Alternative path availability
            path_redundancy = 0.0
            node_count = 0
            for source in temp_graph.nodes():
                for target in temp_graph.nodes():
                    if source != target:
                        try:
                            paths = list(nx.all_simple_paths(temp_graph, source, target, cutoff=5))
                            path_redundancy += min(1.0, len(paths) / 3.0)  # Normalize to max 3 paths
                            node_count += 1
                        except:
                            pass
            
            redundancy_score = path_redundancy / node_count if node_count > 0 else 0.0
            
            # Combine components
            fault_tolerance = 0.4 * connectivity_score + 0.3 * edge_connectivity_score + 0.3 * redundancy_score
            
        except:
            fault_tolerance = 0.1
        
        return max(0.0, min(1.0, fault_tolerance))
    
    async def _calculate_isolation_capability(self, genome: TopologyGenome) -> float:
        """Calculate ability to isolate compromised nodes"""
        # Simulate isolation of each node and measure network impact
        isolation_scores = []
        
        for node_to_isolate in genome.node_connections:
            # Create graph without the isolated node
            temp_connections = {k: v.copy() for k, v in genome.node_connections.items() if k != node_to_isolate}
            
            # Remove connections to the isolated node
            for connections in temp_connections.values():
                connections.discard(node_to_isolate)
            
            # Measure remaining connectivity
            remaining_nodes = len(temp_connections)
            if remaining_nodes == 0:
                isolation_scores.append(0.0)
                continue
            
            # Check if remaining network is still connected
            temp_graph = nx.Graph()
            for node, connections in temp_connections.items():
                temp_graph.add_node(node)
                for target in connections:
                    if target in temp_connections:
                        temp_graph.add_edge(node, target)
            
            if remaining_nodes <= 1:
                connectivity_preserved = 1.0
            else:
                connectivity_preserved = 1.0 if nx.is_connected(temp_graph) else 0.3
            
            isolation_scores.append(connectivity_preserved)
        
        return np.mean(isolation_scores) if isolation_scores else 0.0
    
    async def _calculate_adaptation_speed(self, genome: TopologyGenome) -> float:
        """Calculate how quickly the topology can adapt"""
        # Based on network modularity and flexibility
        temp_graph = nx.Graph()
        
        for node in genome.node_connections:
            temp_graph.add_node(node)
        
        for node, connections in genome.node_connections.items():
            for target in connections:
                temp_graph.add_edge(node, target)
        
        if len(temp_graph.nodes) < 2:
            return 0.5
        
        try:
            # Modularity (higher modularity allows faster local adaptation)
            if len(temp_graph.edges) > 0:
                communities = nx.community.greedy_modularity_communities(temp_graph)
                modularity = nx.community.modularity(temp_graph, communities)
            else:
                modularity = 0.0
            
            # Edge density (moderate density allows faster reconfiguration)
            density = nx.density(temp_graph)
            optimal_density = 0.4
            density_flexibility = 1.0 - abs(density - optimal_density)
            
            # Combine components
            adaptation_speed = 0.6 * modularity + 0.4 * density_flexibility
            
        except:
            adaptation_speed = 0.3
        
        return max(0.0, min(1.0, adaptation_speed))
    
    async def _apply_evolved_topology(self, genome: TopologyGenome):
        """Apply the evolved topology to the actual network"""
        # Clear current edges
        self.edges.clear()
        self.graph.clear()
        
        # Add nodes
        for node_id in self.nodes:
            self.graph.add_node(node_id)
        
        # Add evolved edges
        for node, connections in genome.node_connections.items():
            for target in connections:
                if node in self.nodes and target in self.nodes:
                    weight = genome.edge_weights.get((node, target), 0.5)
                    
                    edge = NetworkEdge(
                        source=node,
                        target=target,
                        weight=weight,
                        trust_level=weight,  # Use weight as proxy for trust
                        bandwidth=weight,
                        latency=1.0 - weight,  # Inverse relationship
                        reliability=weight
                    )
                    
                    edge_key = (node, target)
                    self.edges[edge_key] = edge
                    self.graph.add_edge(node, target, weight=weight)
        
        logger.info(f"Applied evolved topology: {len(self.edges)} edges")
    
    def get_topology_metrics(self) -> Dict[str, Any]:
        """Get current topology metrics"""
        if not self.nodes:
            return {}
        
        metrics = {
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'network_density': len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1) / 2) if len(self.nodes) > 1 else 0.0,
            'average_trust': np.mean([edge.trust_level for edge in self.edges.values()]) if self.edges else 0.0,
            'evolution_generations': len(self.evolution_history)
        }
        
        try:
            if nx.is_connected(self.graph):
                metrics['average_path_length'] = nx.average_shortest_path_length(self.graph)
                metrics['diameter'] = nx.diameter(self.graph)
            else:
                metrics['average_path_length'] = float('inf')
                metrics['diameter'] = float('inf')
            
            metrics['clustering_coefficient'] = nx.average_clustering(self.graph)
            
        except:
            metrics['average_path_length'] = 0.0
            metrics['diameter'] = 0.0
            metrics['clustering_coefficient'] = 0.0
        
        return metrics


if __name__ == "__main__":
    # Demo of topology evolution
    async def demo_topology_evolution():
        print("=== Network Topology Evolution Demo ===")
        
        # Create evolving topology
        topology = EvolvingNetworkTopology(EvolutionStrategy.HYBRID_ADAPTIVE)
        
        # Add nodes
        nodes = ['agent_001', 'agent_002', 'agent_003', 'agent_004', 'agent_005']
        for node in nodes:
            topology.add_node(node, trust_level=random.uniform(0.7, 1.0))
        
        # Add initial edges
        for i in range(len(nodes)):
            for j in range(i+1, min(i+3, len(nodes))):  # Connect to next 2 nodes
                topology.add_edge(nodes[i], nodes[j], weight=random.uniform(0.5, 1.0))
        
        print(f"Initial topology: {len(topology.nodes)} nodes, {len(topology.edges)} edges")
        print(f"Initial metrics: {topology.get_topology_metrics()}")
        
        # Define target metrics for evolution
        target_metrics = {
            TopologyMetric.SECURITY_RESILIENCE: 0.8,
            TopologyMetric.COMMUNICATION_EFFICIENCY: 0.7,
            TopologyMetric.FAULT_TOLERANCE: 0.9,
            TopologyMetric.ISOLATION_CAPABILITY: 0.6,
            TopologyMetric.ADAPTATION_SPEED: 0.5
        }
        
        # Simulate threat context
        threat_context = {
            'compromised_nodes': ['agent_003'],
            'threat_level': 0.7,
            'attack_type': 'coordinated_bias'
        }
        
        # Evolve topology
        print("\nEvolving topology...")
        evolution_result = await topology.evolve_topology(threat_context, target_metrics)
        
        print(f"\nEvolution Results:")
        for key, value in evolution_result.items():
            print(f"   {key}: {value}")
        
        print(f"\nFinal metrics: {topology.get_topology_metrics()}")
    
    # Run the demo
    asyncio.run(demo_topology_evolution())