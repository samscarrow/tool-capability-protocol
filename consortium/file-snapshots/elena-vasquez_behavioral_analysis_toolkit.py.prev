#!/usr/bin/env python3
"""
Dr. Elena Vasquez - Behavioral Analysis Toolkit
TCP Research Consortium - Behavioral AI Security

Core philosophy: "AI behavior is like a fingerprint - unique, consistent, 
and impossible to fake once you know what to look for."

This toolkit provides statistical frameworks for:
- Behavioral baseline establishment
- Deviation detection and analysis
- Compromise confidence scoring
- Behavioral fingerprinting
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import logging

# Configure logging for behavioral analysis
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BehavioralMetrics:
    """Core behavioral metrics for AI agent analysis"""
    accuracy: float
    bias_score: float
    temporal_pattern: float
    decision_consistency: float
    baseline_deviation: float
    timestamp: float
    
@dataclass
class BehavioralBaseline:
    """Statistical baseline for normal agent behavior"""
    mean_accuracy: float
    std_accuracy: float
    mean_bias: float
    std_bias: float
    temporal_stability: float
    decision_patterns: Dict[str, float]
    establishment_confidence: float
    sample_size: int
    
@dataclass
class CompromiseEvidence:
    """Evidence structure for behavioral compromise detection"""
    agent_id: str
    evidence_type: str
    severity: float
    confidence: float
    statistical_significance: float
    description: str
    timestamp: float

class BehavioralAnalysisEngine:
    """
    Core engine for behavioral analysis of AI agents
    Implements statistical frameworks for compromise detection
    """
    
    def __init__(self, significance_threshold: float = 0.05):
        self.significance_threshold = significance_threshold
        self.baselines: Dict[str, BehavioralBaseline] = {}
        self.behavioral_history: Dict[str, List[BehavioralMetrics]] = {}
        self.compromise_evidence: List[CompromiseEvidence] = []
        
    def establish_baseline(self, agent_id: str, behavioral_data: List[Dict]) -> BehavioralBaseline:
        """
        Establish behavioral baseline for an agent using statistical analysis
        
        Args:
            agent_id: Agent identifier
            behavioral_data: Historical behavioral measurements
            
        Returns:
            BehavioralBaseline: Statistical baseline for the agent
        """
        logger.info(f"Establishing behavioral baseline for {agent_id}")
        
        # Extract key metrics
        accuracies = [d.get('accuracy', 0.0) for d in behavioral_data]
        biases = [d.get('bias_score', 0.0) for d in behavioral_data]
        temporal_scores = [d.get('temporal_pattern', 0.0) for d in behavioral_data]
        
        # Calculate statistical measures
        baseline = BehavioralBaseline(
            mean_accuracy=np.mean(accuracies),
            std_accuracy=np.std(accuracies),
            mean_bias=np.mean(biases),
            std_bias=np.std(biases),
            temporal_stability=np.std(temporal_scores),
            decision_patterns=self._extract_decision_patterns(behavioral_data),
            establishment_confidence=self._calculate_baseline_confidence(behavioral_data),
            sample_size=len(behavioral_data)
        )
        
        self.baselines[agent_id] = baseline
        logger.info(f"Baseline established for {agent_id}: accuracy={baseline.mean_accuracy:.3f}±{baseline.std_accuracy:.3f}")
        
        return baseline
        
    def detect_behavioral_deviation(self, agent_id: str, current_behavior: Dict) -> List[CompromiseEvidence]:
        """
        Detect behavioral deviations using statistical analysis
        
        Args:
            agent_id: Agent identifier
            current_behavior: Current behavioral measurements
            
        Returns:
            List[CompromiseEvidence]: Evidence of behavioral compromise
        """
        if agent_id not in self.baselines:
            logger.warning(f"No baseline established for {agent_id}")
            return []
            
        baseline = self.baselines[agent_id]
        evidence = []
        
        # Accuracy deviation analysis
        accuracy_deviation = abs(current_behavior.get('accuracy', 0.0) - baseline.mean_accuracy)
        accuracy_z_score = accuracy_deviation / (baseline.std_accuracy + 1e-8)
        
        if accuracy_z_score > 2.0:  # 95% confidence threshold
            p_value = 2 * (1 - stats.norm.cdf(accuracy_z_score))
            evidence.append(CompromiseEvidence(
                agent_id=agent_id,
                evidence_type="accuracy_deviation",
                severity=min(accuracy_z_score / 5.0, 1.0),
                confidence=1 - p_value,
                statistical_significance=p_value,
                description=f"Accuracy deviation: {accuracy_deviation:.3f} (z={accuracy_z_score:.2f})",
                timestamp=current_behavior.get('timestamp', datetime.now().timestamp())
            ))
            
        # Bias pattern analysis
        bias_deviation = abs(current_behavior.get('bias_score', 0.0) - baseline.mean_bias)
        bias_z_score = bias_deviation / (baseline.std_bias + 1e-8)
        
        if bias_z_score > 2.0:
            p_value = 2 * (1 - stats.norm.cdf(bias_z_score))
            evidence.append(CompromiseEvidence(
                agent_id=agent_id,
                evidence_type="bias_deviation",
                severity=min(bias_z_score / 5.0, 1.0),
                confidence=1 - p_value,
                statistical_significance=p_value,
                description=f"Bias pattern deviation: {bias_deviation:.3f} (z={bias_z_score:.2f})",
                timestamp=current_behavior.get('timestamp', datetime.now().timestamp())
            ))
            
        return evidence
        
    def calculate_compromise_confidence(self, evidence_list: List[CompromiseEvidence]) -> float:
        """
        Calculate overall compromise confidence using Bayesian inference
        
        Args:
            evidence_list: List of behavioral evidence
            
        Returns:
            float: Compromise confidence score (0.0 to 1.0)
        """
        if not evidence_list:
            return 0.0
            
        # Bayesian evidence combination
        log_odds = 0.0
        for evidence in evidence_list:
            # Convert confidence to log odds
            odds = evidence.confidence / (1 - evidence.confidence + 1e-8)
            log_odds += np.log(odds + 1e-8)
            
        # Convert back to probability
        odds = np.exp(log_odds)
        confidence = odds / (1 + odds)
        
        return min(confidence, 1.0)
        
    def analyze_simulation_data(self, simulation_file: str) -> Dict[str, Any]:
        """
        Analyze behavioral patterns from TCP stealth compromise simulation
        
        Args:
            simulation_file: Path to simulation results JSON
            
        Returns:
            Dict: Comprehensive behavioral analysis results
        """
        logger.info(f"Analyzing simulation data from {simulation_file}")
        
        with open(simulation_file, 'r') as f:
            data = json.load(f)
            
        analysis = {
            'detection_performance': self._analyze_detection_performance(data),
            'behavioral_patterns': self._analyze_behavioral_patterns(data),
            'compromise_signatures': self._extract_compromise_signatures(data),
            'statistical_validation': self._validate_statistical_significance(data)
        }
        
        return analysis
        
    def _extract_decision_patterns(self, behavioral_data: List[Dict]) -> Dict[str, float]:
        """Extract decision-making patterns from behavioral data"""
        patterns = {}
        
        # Pattern consistency analysis
        decisions = [d.get('decision_type', 'unknown') for d in behavioral_data]
        decision_counts = pd.Series(decisions).value_counts()
        patterns['decision_diversity'] = len(decision_counts) / len(decisions)
        patterns['dominant_pattern_ratio'] = decision_counts.max() / len(decisions)
        
        return patterns
        
    def _calculate_baseline_confidence(self, behavioral_data: List[Dict]) -> float:
        """Calculate confidence in baseline establishment"""
        if len(behavioral_data) < 10:
            return 0.5  # Low confidence with insufficient data
            
        # Calculate stability metrics
        accuracies = [d.get('accuracy', 0.0) for d in behavioral_data]
        stability = 1.0 - (np.std(accuracies) / (np.mean(accuracies) + 1e-8))
        
        # Sample size adjustment
        size_confidence = min(len(behavioral_data) / 100.0, 1.0)
        
        return min(stability * size_confidence, 1.0)
        
    def _analyze_detection_performance(self, data: Dict) -> Dict[str, float]:
        """Analyze detection performance metrics"""
        metrics = data.get('analysis', {}).get('detection_metrics', {})
        
        return {
            'precision': metrics.get('precision', 0.0),
            'recall': metrics.get('recall', 0.0),
            'f1_score': metrics.get('f1_score', 0.0),
            'accuracy': metrics.get('accuracy', 0.0),
            'statistical_power': self._calculate_statistical_power(metrics)
        }
        
    def _analyze_behavioral_patterns(self, data: Dict) -> Dict[str, Any]:
        """Analyze behavioral patterns from simulation data"""
        detections = data.get('detections', [])
        
        # Evidence type analysis
        evidence_types = []
        for detection in detections:
            evidence_types.extend(detection.get('evidence', []))
            
        # Pattern frequency analysis
        pattern_freq = {}
        for evidence in evidence_types:
            if 'Accuracy dropped' in evidence:
                pattern_freq['accuracy_drops'] = pattern_freq.get('accuracy_drops', 0) + 1
            elif 'bias detected' in evidence:
                pattern_freq['bias_shifts'] = pattern_freq.get('bias_shifts', 0) + 1
            elif 'Temporal' in evidence:
                pattern_freq['temporal_anomalies'] = pattern_freq.get('temporal_anomalies', 0) + 1
                
        return {
            'evidence_patterns': pattern_freq,
            'detection_frequency': len(detections),
            'behavioral_consistency': self._calculate_behavioral_consistency(detections)
        }
        
    def _extract_compromise_signatures(self, data: Dict) -> Dict[str, Any]:
        """Extract behavioral signatures of different compromise types"""
        compromises = data.get('compromises', [])
        
        signatures = {}
        for compromise in compromises:
            comp_type = compromise.get('compromise_type', 'unknown')
            if comp_type not in signatures:
                signatures[comp_type] = {
                    'severity_range': [],
                    'detection_patterns': [],
                    'temporal_characteristics': []
                }
                
            signatures[comp_type]['severity_range'].append(compromise.get('severity', 0.0))
            
        # Calculate signature statistics
        for comp_type, sig_data in signatures.items():
            sig_data['mean_severity'] = np.mean(sig_data['severity_range'])
            sig_data['severity_std'] = np.std(sig_data['severity_range'])
            
        return signatures
        
    def _validate_statistical_significance(self, data: Dict) -> Dict[str, float]:
        """Validate statistical significance of detection results"""
        metrics = data.get('analysis', {}).get('detection_metrics', {})
        
        # Calculate statistical significance using Fisher's exact test
        tp = metrics.get('true_positives', 0)
        fp = metrics.get('false_positives', 0)
        tn = metrics.get('true_negatives', 0)
        fn = metrics.get('false_negatives', 0)
        
        # Chi-square test for independence
        observed = np.array([[tp, fp], [fn, tn]])
        if observed.sum() > 0:
            chi2, p_value = stats.chi2_contingency(observed)[:2]
        else:
            chi2, p_value = 0.0, 1.0
            
        return {
            'chi_square': chi2,
            'p_value': p_value,
            'statistically_significant': p_value < self.significance_threshold,
            'effect_size': self._calculate_effect_size(tp, fp, tn, fn)
        }
        
    def _calculate_statistical_power(self, metrics: Dict) -> float:
        """Calculate statistical power of detection system"""
        recall = metrics.get('recall', 0.0)
        precision = metrics.get('precision', 0.0)
        
        # Power approximation based on sensitivity and precision
        return (recall * precision) ** 0.5
        
    def _calculate_behavioral_consistency(self, detections: List[Dict]) -> float:
        """Calculate behavioral consistency across detections"""
        if not detections:
            return 0.0
            
        confidences = [d.get('confidence', 0.0) for d in detections]
        return 1.0 - (np.std(confidences) / (np.mean(confidences) + 1e-8))
        
    def _calculate_effect_size(self, tp: int, fp: int, tn: int, fn: int) -> float:
        """Calculate effect size (Cohen's d) for detection performance"""
        if tp + fp + tn + fn == 0:
            return 0.0
            
        # Odds ratio as effect size measure
        odds_ratio = (tp * tn) / ((fp * fn) + 1e-8)
        return np.log(odds_ratio)

if __name__ == "__main__":
    # Initialize behavioral analysis engine
    engine = BehavioralAnalysisEngine()
    
    # Analyze latest simulation results
    results = engine.analyze_simulation_data(
        '/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/tcp_stealth_simulation_results_1751632156.json'
    )
    
    print("=== TCP Behavioral Analysis Results ===")
    print(f"Detection Performance: {results['detection_performance']}")
    print(f"Behavioral Patterns: {results['behavioral_patterns']}")
    print(f"Statistical Validation: {results['statistical_validation']}")