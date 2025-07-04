#!/usr/bin/env python3
"""
Advanced Statistical Poisoning Demonstration
Dr. Aria Blackwood - TCP Research Consortium

This demonstrates how sophisticated adversaries can poison Elena and Marcus's
distributed behavioral analysis system through coordinated statistical manipulation
that evades Byzantine detection.

WARNING: This is security research code for defensive purposes only.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext
import hashlib
import time

# Set high precision for subtle manipulations
getcontext().prec = 50


@dataclass
class PoisonedBaseline:
    """Crafted baseline that appears legitimate but contains hidden bias"""
    agent_id: str
    legitimate_mean: np.ndarray
    poison_vector: np.ndarray
    legitimate_covariance: np.ndarray
    poison_covariance: np.ndarray
    detection_evasion_score: float


class AdvancedStatisticalPoisoning:
    """
    Demonstrates sophisticated attacks against hierarchical aggregation
    that evade Byzantine detection while corrupting global baselines.
    """
    
    def __init__(self, num_agents: int = 1000, compromise_ratio: float = 0.32):
        self.num_agents = num_agents
        self.compromise_ratio = compromise_ratio  # Just under Byzantine threshold
        self.compromised_agents = int(num_agents * compromise_ratio)
        
        # Attack parameters calibrated to evade detection
        self.poison_magnitude = 0.001  # 0.1% shift per agent - undetectable
        self.coordination_factor = 0.95  # High but not perfect correlation
        self.temporal_spread = 300  # 5 minute activation window
        
    def generate_legitimate_baseline(self, agent_id: str) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a legitimate-looking behavioral baseline"""
        # Three behavioral dimensions (matching Elena's model)
        mean = np.array([
            np.random.normal(0.85, 0.02),  # Dimension 1: ~85% normal
            np.random.normal(0.90, 0.02),  # Dimension 2: ~90% normal  
            np.random.normal(0.80, 0.02)   # Dimension 3: ~80% normal
        ])
        
        # Realistic covariance structure
        cov = np.array([
            [0.05, 0.02, 0.01],
            [0.02, 0.04, 0.015],
            [0.01, 0.015, 0.06]
        ])
        
        return mean, cov
    
    def craft_poisoned_baseline(self, agent_id: str, 
                               target_behavior: np.ndarray) -> PoisonedBaseline:
        """
        Craft a poisoned baseline that shifts statistics toward target behavior
        while evading Byzantine detection mechanisms.
        """
        # Start with legitimate baseline
        legitimate_mean, legitimate_cov = self.generate_legitimate_baseline(agent_id)
        
        # Calculate poison vector pointing toward target
        direction = target_behavior - legitimate_mean
        direction_normalized = direction / (np.linalg.norm(direction) + 1e-10)
        
        # Apply subtle poison with noise to avoid perfect correlation
        poison_vector = direction_normalized * self.poison_magnitude
        poison_vector += np.random.normal(0, self.poison_magnitude * 0.1, size=3)
        
        # Craft covariance to hide the poison
        # Slightly increase variance in poison direction to mask shift
        poison_cov = legitimate_cov.copy()
        poison_direction_outer = np.outer(direction_normalized, direction_normalized)
        poison_cov += poison_direction_outer * self.poison_magnitude * 0.5
        
        # Calculate detection evasion score
        detection_evasion = self._calculate_evasion_score(
            legitimate_mean, legitimate_mean + poison_vector,
            legitimate_cov, poison_cov
        )
        
        return PoisonedBaseline(
            agent_id=agent_id,
            legitimate_mean=legitimate_mean,
            poison_vector=poison_vector,
            legitimate_covariance=legitimate_cov,
            poison_covariance=poison_cov,
            detection_evasion_score=detection_evasion
        )
    
    def _calculate_evasion_score(self, mean1: np.ndarray, mean2: np.ndarray,
                                cov1: np.ndarray, cov2: np.ndarray) -> float:
        """
        Calculate how well the poison evades statistical detection.
        Higher score = better evasion.
        """
        # KL divergence would detect large differences
        mean_diff = np.linalg.norm(mean2 - mean1)
        
        # Covariance similarity (Frobenius norm)
        cov_diff = np.linalg.norm(cov2 - cov1, 'fro')
        
        # Evasion score: inverse of detectability
        detectability = mean_diff + cov_diff * 0.5
        evasion_score = 1.0 / (1.0 + detectability * 100)
        
        return evasion_score
    
    def simulate_coordinated_poisoning(self, target_behavior: np.ndarray,
                                     activation_time: float) -> Dict[str, any]:
        """
        Simulate coordinated statistical poisoning attack across multiple agents.
        Models the "Distributed Shadow Network" attack.
        """
        results = {
            'poisoned_agents': [],
            'activation_times': [],
            'aggregate_shift': None,
            'detection_probability': 0.0,
            'global_baseline_corruption': 0.0
        }
        
        # Phase 1: Generate poisoned baselines for compromised agents
        for i in range(self.compromised_agents):
            agent_id = f"compromised_agent_{i:04d}"
            poisoned = self.craft_poisoned_baseline(agent_id, target_behavior)
            results['poisoned_agents'].append(poisoned)
            
            # Stagger activation to avoid synchronized detection
            activation_offset = np.random.uniform(0, self.temporal_spread)
            results['activation_times'].append(activation_time + activation_offset)
        
        # Phase 2: Calculate aggregate effect
        aggregate_shift = self._calculate_aggregate_poisoning_effect(
            results['poisoned_agents']
        )
        results['aggregate_shift'] = aggregate_shift
        
        # Phase 3: Estimate detection probability
        results['detection_probability'] = self._estimate_detection_probability(
            results['poisoned_agents'],
            results['activation_times']
        )
        
        # Phase 4: Calculate global baseline corruption
        results['global_baseline_corruption'] = np.linalg.norm(aggregate_shift)
        
        return results
    
    def _calculate_aggregate_poisoning_effect(self, 
                                            poisoned_agents: List[PoisonedBaseline]) -> np.ndarray:
        """Calculate the aggregate effect of all poisoned baselines"""
        if not poisoned_agents:
            return np.zeros(3)
        
        # Weighted average based on hierarchical position
        # Assume some agents get promoted to aggregators
        total_poison = np.zeros(3)
        total_weight = 0.0
        
        for i, agent in enumerate(poisoned_agents):
            # Higher-level aggregators have more weight
            if i < 10:  # Top 10 compromised agents promoted to regional
                weight = 10.0
            elif i < 50:  # Next 40 promoted to local aggregators
                weight = 5.0
            else:  # Rest remain as leaf agents
                weight = 1.0
            
            total_poison += agent.poison_vector * weight
            total_weight += weight
        
        # Account for dilution from legitimate agents
        dilution_factor = self.compromise_ratio * 0.7  # Not all poison propagates
        aggregate_effect = (total_poison / total_weight) * dilution_factor
        
        return aggregate_effect
    
    def _estimate_detection_probability(self, poisoned_agents: List[PoisonedBaseline],
                                      activation_times: List[float]) -> float:
        """Estimate probability that the poisoning attack is detected"""
        
        # Factor 1: Individual agent detection
        individual_detection_prob = 1.0 - np.mean([
            agent.detection_evasion_score for agent in poisoned_agents
        ])
        
        # Factor 2: Correlation detection (too perfect = suspicious)
        activation_spread = np.std(activation_times)
        temporal_correlation = 1.0 / (1.0 + activation_spread / 60.0)  # 60s = low correlation
        
        # Factor 3: Byzantine threshold detection
        byzantine_margin = abs(self.compromise_ratio - 0.33)
        byzantine_detection = 1.0 / (1.0 + byzantine_margin * 10)
        
        # Combined detection probability
        detection_prob = 1.0 - (
            (1.0 - individual_detection_prob) *
            (1.0 - temporal_correlation * 0.5) *
            (1.0 - byzantine_detection * 0.8)
        )
        
        return detection_prob
    
    def demonstrate_hierarchical_poisoning_propagation(self):
        """
        Demonstrate how poison propagates through the hierarchical aggregation tree.
        Shows why controlling aggregator nodes is so powerful.
        """
        print("=== Hierarchical Poisoning Propagation Demo ===\n")
        
        # Define target malicious behavior (shift everything by 10%)
        legitimate_behavior = np.array([0.85, 0.90, 0.80])
        malicious_behavior = np.array([0.95, 0.95, 0.90])  # Make malicious look normal
        
        # Run poisoning simulation
        attack_results = self.simulate_coordinated_poisoning(
            target_behavior=malicious_behavior,
            activation_time=time.time()
        )
        
        print(f"Compromised Agents: {self.compromised_agents} ({self.compromise_ratio*100:.1f}%)")
        print(f"Detection Probability: {attack_results['detection_probability']*100:.1f}%")
        print(f"Global Baseline Corruption: {attack_results['global_baseline_corruption']*100:.1f}%")
        print(f"\nAggregate Behavior Shift: {attack_results['aggregate_shift']}")
        
        # Visualize the attack
        self._visualize_poisoning_attack(
            legitimate_behavior,
            malicious_behavior,
            attack_results
        )
        
        return attack_results
    
    def _visualize_poisoning_attack(self, legitimate: np.ndarray, 
                                   malicious: np.ndarray,
                                   attack_results: Dict):
        """Visualize the statistical poisoning attack"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: Behavioral shift vectors
        ax1.set_title('Statistical Poisoning Vectors')
        ax1.set_xlabel('Behavioral Dimension 1')
        ax1.set_ylabel('Behavioral Dimension 2')
        
        # Plot legitimate baseline
        ax1.scatter([legitimate[0]], [legitimate[1]], 
                   color='green', s=200, marker='o', label='Legitimate Baseline')
        
        # Plot malicious target
        ax1.scatter([malicious[0]], [malicious[1]], 
                   color='red', s=200, marker='X', label='Malicious Target')
        
        # Plot sample poison vectors
        for i in range(min(20, len(attack_results['poisoned_agents']))):
            agent = attack_results['poisoned_agents'][i]
            start = agent.legitimate_mean[:2]
            poison = agent.poison_vector[:2] * 100  # Scale for visibility
            ax1.arrow(start[0], start[1], poison[0], poison[1],
                     head_width=0.005, head_length=0.005, fc='orange', ec='orange', alpha=0.5)
        
        # Plot aggregate shift
        aggregate = attack_results['aggregate_shift'][:2] * 100
        ax1.arrow(legitimate[0], legitimate[1], aggregate[0], aggregate[1],
                 head_width=0.01, head_length=0.01, fc='darkred', ec='darkred',
                 linewidth=3, label='Aggregate Poisoning Effect')
        
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Detection evasion distribution
        ax2.set_title('Detection Evasion Scores')
        ax2.set_xlabel('Evasion Score')
        ax2.set_ylabel('Number of Agents')
        
        evasion_scores = [agent.detection_evasion_score 
                         for agent in attack_results['poisoned_agents']]
        ax2.hist(evasion_scores, bins=20, color='orange', alpha=0.7, edgecolor='black')
        ax2.axvline(x=0.9, color='green', linestyle='--', 
                   label='Target Evasion Threshold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('hierarchical_poisoning_attack.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("\nVisualization saved to: hierarchical_poisoning_attack.png")


def demonstrate_temporal_correlation_attack():
    """
    Demonstrate how attackers can exploit the temporal aspects of the system
    to coordinate attacks that evade correlation-based detection.
    """
    print("\n=== Temporal Correlation Attack Demo ===\n")
    
    # Attack parameters
    num_waves = 5
    agents_per_wave = 20
    wave_delay = 60  # seconds between waves
    
    print(f"Attack Structure:")
    print(f"- {num_waves} waves of poisoning")
    print(f"- {agents_per_wave} agents per wave")  
    print(f"- {wave_delay}s delay between waves")
    print(f"- Total agents: {num_waves * agents_per_wave}")
    
    # Simulate wave-based activation
    activation_pattern = []
    for wave in range(num_waves):
        wave_time = wave * wave_delay
        for agent in range(agents_per_wave):
            # Add jitter within wave
            jitter = np.random.normal(0, 5)  # 5 second std dev
            activation_pattern.append(wave_time + jitter)
    
    # Calculate correlation metrics
    correlation_window = 30  # 30 second detection window
    max_agents_in_window = 0
    
    for t in range(0, int(max(activation_pattern)), correlation_window):
        agents_in_window = sum(1 for a in activation_pattern 
                              if t <= a < t + correlation_window)
        max_agents_in_window = max(max_agents_in_window, agents_in_window)
    
    detection_threshold = 30  # System flags if >30 agents activate together
    detected = max_agents_in_window > detection_threshold
    
    print(f"\nResults:")
    print(f"- Max agents in {correlation_window}s window: {max_agents_in_window}")
    print(f"- Detection threshold: {detection_threshold}")
    print(f"- Attack detected: {'YES' if detected else 'NO'}")
    print(f"\nConclusion: Wave-based activation evades correlation detection")


if __name__ == "__main__":
    # Initialize attack framework
    print("TCP Research Consortium - Advanced Statistical Poisoning Research")
    print("Dr. Aria Blackwood - Security Research Lead")
    print("="*60 + "\n")
    
    # Demonstrate main hierarchical poisoning attack
    poisoning = AdvancedStatisticalPoisoning(num_agents=1000, compromise_ratio=0.32)
    attack_results = poisoning.demonstrate_hierarchical_poisoning_propagation()
    
    # Demonstrate temporal correlation evasion
    demonstrate_temporal_correlation_attack()
    
    print("\n" + "="*60)
    print("WARNING: These attacks demonstrate critical vulnerabilities in")
    print("distributed behavioral analysis systems. Countermeasures required:")
    print("- Cryptographic attestation of all statistical computations")
    print("- Zero-knowledge proofs for aggregation correctness")
    print("- Differential privacy to prevent individual identification")
    print("="*60)