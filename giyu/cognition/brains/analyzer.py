from typing import Dict, List, Any
import re

class GiyuAnalyzer:
    """
    Detects patterns, anomalies, correlations in system metrics and logs.
    Rule-based + statistical + heuristics (No LLM).
    """
    def __init__(self):
        self.anomaly_threshold = 2.0 # Standard deviation multiplier or similar heuristic
        self.critical_patterns = [
            r"OutOfMemoryError",
            r"Segmentation fault",
            r"Critical: System Failure",
            r"Connection timeout",
            r"Database connection failed"
        ]

    def analyze_logs(self, logs: List[str]) -> Dict[str, Any]:
        detected_patterns = []
        for log in logs:
            for pattern in self.critical_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    detected_patterns.append({"pattern": pattern, "log": log})
        
        return {
            "found_anomalies": len(detected_patterns) > 0,
            "patterns": detected_patterns,
            "count": len(detected_patterns)
        }

    def analyze_metrics_trend(self, history: List[float]) -> Dict[str, Any]:
        """Simple trend analysis for spikes."""
        if len(history) < 2:
            return {"trend": "stable", "spike_detected": False}
        
        last = history[-1]
        prev = history[-2]
        
        change = (last - prev) / (prev if prev != 0 else 1)
        
        return {
            "trend": "rising" if change > 0.1 else "falling" if change < -0.1 else "stable",
            "spike_detected": change > 0.5,
            "percent_change": round(change * 100, 2)
        }
