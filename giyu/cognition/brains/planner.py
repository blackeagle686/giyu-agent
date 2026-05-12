from phoenix.framework.agent.cognition import Planner
import json
import re

from ..helpers.tasks import _clean_json
from ..helpers.plan import _load_plan, _save_plan
from ..core.prompts import PLAN_GENERATION_PROMPT

class GiyuPlanner(Planner):
    """
    Receives one task at a time and generates a sequence of plan_steps.
    Persists to giyu.plan.json and does NOT generate tool actions directly.
    """

    def __init__(self, llm, tools, system_info: str = ""):
        super().__init__(llm, tools)
        self.system_info = system_info

    async def generate_plan_steps(self, task: dict) -> list:
        """
        Ask LLM to generate plan steps for the given task and persist to the backbone.
        """
        from ..helpers.schemas import validate_schema, PLAN_SCHEMA
        
        # Inject system context for optimized task handling
        sys_context = f"\n[SYSTEM CONTEXT]\n{self.system_info}\n" if self.system_info else ""
        
        prompt = PLAN_GENERATION_PROMPT.format(
            task_id=task.get("id", 1),
            priority=task.get("priority", 1),
            title=task.get("title", ""),
            description=task.get("description", "") + sys_context
        )

        response = await self.llm.generate(prompt, session_id=None)
        clean = _clean_json(response)
        
        try:
            plan_data = json.loads(clean)
        except Exception as e:
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m:
                try:
                    plan_data = json.loads(m.group(0))
                except Exception:
                    plan_data = {"plan_steps": []}
            else:
                plan_data = {"plan_steps": []}

        # Schema Validation
        errors = validate_schema(plan_data, PLAN_SCHEMA)
        if errors:
            print(f"[PLANNER WARNING] Schema validation failed: {errors}")
                
        new_steps = plan_data.get("plan_steps", [])
        
        # Automatically assign unique integer plan_step_ids
        existing_plan = _load_plan()
        existing_steps = existing_plan.get("plan_steps", [])
        
        id_map = {}
        next_step_id = 1
        if existing_steps:
            next_step_id = max((s.get("plan_step_id", 0) for s in existing_steps)) + 1
            
        for step in new_steps:
            old_id = step.get("plan_step_id")
            if old_id is not None:
                id_map[old_id] = next_step_id
            
            # Force task_id to match the current task
            step["task_id"] = task.get("id", 1)
            # Re-assign IDs to prevent collisions
            step["plan_step_id"] = next_step_id
            step["status"] = "pending"
            next_step_id += 1
            
        # Remap dependencies
        for step in new_steps:
            old_deps = step.get("dependencies", [])
            new_deps = []
            for dep in old_deps:
                if dep in id_map:
                    new_deps.append(id_map[dep])
                else:
                    new_deps.append(dep)
            step["dependencies"] = new_deps
            
        existing_steps.extend(new_steps)
        existing_plan["plan_steps"] = existing_steps
        _save_plan(existing_plan)
        
        # Generate a high-level summary for the user
        await self.generate_summary_report(task, new_steps)
        
        return new_steps

    async def generate_summary_report(self, task: dict, steps: list) -> None:
        """
        Generates a readable high-level report of the plan for the user.
        """
        step_descriptions = "\n".join([f"- {s.get('description')}" for s in steps])
        report_prompt = f"""
        Generate a concise, professional summary report for the user based on the following task and planned steps.
        Focus on the GOAL and the RESULT. Avoid technical jargon where possible.
        
        TASK: {task.get('title')}
        DESCRIPTION: {task.get('description')}
        
        PLANNED STEPS:
        {step_descriptions}
        
        Format as a clean markdown report.
        """
        report = await self.llm.generate(report_prompt, session_id=None)
        # We can print this to the console or store it in the task object
        print(f"\n[GIYU SENTINEL REPORT]\n{report}\n")
        task["summary_report"] = report

    def task_status_line(self, task: dict) -> str:
        """Return a deterministic status line from the task dict — no LLM call needed."""
        type_icon = {"new_file": "📄", "modify_file": "✏️", "command": "⚡", "read": "🔍"}
        icon = type_icon.get(task.get("type", ""), "⚙")
        return f"{icon} {task.get('description', task.get('title', ''))[:120]}"

    async def plan(self, objective: str, previous_results: str = "") -> dict:
        """Fallback if called directly by generic agents. Not typically used in GiyuLoop."""
        return {"actions": [{"tool": "finish"}]}
