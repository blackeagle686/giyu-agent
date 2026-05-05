import time
from typing import Dict, Any

class StabilityScorer:
    """
    Computes system health score and stability state.
    Deterministic (No LLM).
    """
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or {
            "cpu_critical": 90.0,
            "ram_critical": 90.0,
            "disk_critical": 95.0,
            "cpu_warning": 75.0,
            "ram_warning": 75.0
        }

    def compute_score(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates a stability score from 0 to 100.
        100 = Perfect Stability, 0 = System Failure.
        """
        cpu = metrics.get("cpu_usage", 0.0)
        ram = metrics.get("ram_usage", 0.0)
        disk = metrics.get("disk_usage", 0.0)
        
        # Base score
        score = 100.0
        
        # Deductions based on critical thresholds
        if cpu > self.thresholds["cpu_critical"]:
            score -= 40
        elif cpu > self.thresholds["cpu_warning"]:
            score -= 15
            
        if ram > self.thresholds["ram_critical"]:
            score -= 40
        elif ram > self.thresholds["ram_warning"]:
            score -= 15
            
        if disk > self.thresholds["disk_critical"]:
            score -= 20
            
        # Clamp score
        score = max(0.0, min(100.0, score))
        
        state = "stable"
        if score < 40:
            state = "critical"
        elif score < 70:
            state = "unstable"
        elif score < 90:
            state = "degraded"
            
        return {
            "score": score,
            "state": state,
            "timestamp": time.time(),
            "metrics_evaluated": ["cpu", "ram", "disk"]
        }
