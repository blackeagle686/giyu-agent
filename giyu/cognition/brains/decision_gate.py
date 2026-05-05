from typing import Dict, Any

class DecisionGate:
    """
    Decides escalation level (ignore / warn / escalate / emergency).
    Strict rules engine (No LLM).
    """
    def __init__(self):
        self.rules = [
            {"condition": lambda s: s < 20, "action": "emergency"},
            {"condition": lambda s: s < 50, "action": "escalate"},
            {"condition": lambda s: s < 80, "action": "warn"},
            {"condition": lambda s: s >= 80, "action": "ignore"}
        ]

    def evaluate(self, stability_data: Dict[str, Any]) -> Dict[str, Any]:
        score = stability_data.get("score", 100)
        
        selected_action = "ignore"
        for rule in self.rules:
            if rule["condition"](score):
                selected_action = rule["action"]
                break
        
        return {
            "escalation_level": selected_action,
            "necessity": "high" if selected_action in ["emergency", "escalate"] else "low",
            "decision_reason": f"Stability score is {score}"
        }
