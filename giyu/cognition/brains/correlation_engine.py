from typing import List, Dict, Any
from phoenix.framework.agent.cognition.utils.json import parse_llm_json

class CorrelationEngine:
    """
    Links multiple events to detect root cause chains.
    Hybrid mode (Uses LLM).
    """
    def __init__(self, llm):
        self.llm = llm

    async def correlate(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Uses LLM to find links between events.
        """
        events_str = "\n".join([str(e) for e in events])
        
        system_prompt = """
        You are the 'Correlation Engine' for a system stability agent.
        Your job is to look at multiple system events/logs and identify if they are linked 
        in a causal chain. Identify the 'Root Cause'.
        
        Respond with JSON:
        {
            "linked": boolean,
            "root_cause": "description",
            "chain": ["event_a -> event_b"],
            "confidence": 0.0-1.0
        }
        """
        
        prompt = f"{system_prompt}\n\nEvents:\n{events_str}\n\nAnalysis (JSON):"
        response = await self.llm.generate(prompt, session_id=None)
        
        return parse_llm_json(response) or {
            "linked": False,
            "root_cause": "Unknown",
            "chain": [],
            "confidence": 0.0
        }
