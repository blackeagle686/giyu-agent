from phoenix.framework.agent.cognition import Thinker
import json
import re

from ..helpers.tasks import TASK_FILE, _save_tasks, _clean_json
from ..core.prompts import TASK_GENERATION_PROMPT

class GiyuThinker(Thinker):
    """
    Interprets system signals and understands context of events.
    Uses LLM for light reasoning/classification.
    """

    async def analyze(self, prompt: str, memory, session_id: str) -> str:
        from ..helpers.schemas import validate_schema, TASK_SCHEMA
        context = await memory.get_full_context(session_id, query=prompt)

        profile_str = self.profile.to_prompt_string() if self.profile else ""

        system_prompt = f"""
{profile_str}

You are the 'Thinker' module for Giyu Tomioka, the System Stability Guardian.
Your job is to interpret the user's request or system signal and break it down into structured tasks.
Focus on: Stability Monitoring, Anomaly Detection, and Diagnostic Reporting.

Respond with exactly this JSON format:
{{
    "original_prompt": "{prompt}",
    "tasks": [
        {{
            "id": 1,
            "priority": 1,
            "title": "Task Title",
            "description": "Detailed description",
            "status": "pending",
            "type": "read|command|analysis"
        }}
    ]
}}
"""

        raw = await self.llm.generate(f"{system_prompt}\n\nSignal/Prompt: {prompt}\nContext: {context}", session_id=None, max_tokens=500)
        clean = _clean_json(raw)

        # Parse the task list
        try:
            task_data = json.loads(clean)
        except Exception:
            # Fallback
            task_data = {
                "original_prompt": prompt,
                "tasks": [{"id": 1, "priority": 1, "title": "System Health Check", "description": f"Perform diagnostic for: {prompt}", "status": "pending", "type": "analysis"}]
            }

        # Write task file
        _save_tasks(task_data)

        return f"STABILITY_MODE: {prompt[:50]}..."
