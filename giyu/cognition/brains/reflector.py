from phoenix.framework.agent.cognition import Reflector
import json
import re

from ..core.prompts import build_reflector_prompt

class GiyuReflector(Reflector):
    """
    Evaluates historical system behavior and outcomes.
    Summarization + Reasoning over logs.
    """

    async def reflect(self, objective: str, action: dict, result: str) -> dict:
        result_str = str(result)

        profile_str = self.profile.to_prompt_string() if self.profile else ""

        system_prompt = f"""
{profile_str}

You are the 'Reflector' module for Giyu Tomioka.
Your job is to evaluate the outcome of a diagnostic task or system intervention.
Analyze the result for stability implications, hidden errors, or successful stabilization.

Respond with exactly this JSON format:
{{
    "is_complete": boolean,
    "reflection": "Diagnostic summary and reasoning over logs/results",
    "stability_impact": "positive|neutral|negative"
}}
"""

        prompt = f"{system_prompt}\n\nObjective: {objective}\nAction: {action}\nResult: {result_str}"
        response = await self.llm.generate(prompt, session_id=None, max_tokens=300)
        
        try:
            from ..helpers.tasks import _clean_json
            clean = _clean_json(response)
            data = json.loads(clean)
            return {
                "is_complete": bool(data.get("is_complete", False)),
                "reflection": str(data.get("reflection", "")),
                "stability_impact": data.get("stability_impact", "neutral")
            }
        except Exception:
            return {"is_complete": True, "reflection": "Task finalized based on raw output.", "stability_impact": "neutral"}
