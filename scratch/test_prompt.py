
PLAN_GENERATION_PROMPT = """\\
You are the GIYU Planning Engine. You receive ONE task and must break it down into logical execution steps.

=== STRICT DIRECTIVES ===
1. Respond ONLY with valid JSON.
2. No preambles or post-commentary.
3. Use exactly four core types: analysis, design, implementation, validation.
4. Each step must have a clear "solution" object.
5. MONITORING PREFERENCE: For diagnostic and monitoring tasks, always prioritize using CLI commands (via `run_shell_command`) over writing new Python scripts.
6. Only generate code if no existing tool or command can perform the measurement.

Task Info:
Task ID: {task_id}
Priority: {priority}
Title: {title}
Description: {description}

=== RESPONSE SCHEMA ===
{{
  "plan_steps": [
    {{
      "plan_step_id": <INT>,
      "task_id": {task_id},
      "step_index": <INT>,
      "type": "analysis | design | implementation | validation",
      "solution": {{
        "approach": "<detailed text explanation>",
        "algorithm": "<optional>",
        "complexity": "<optional>"
      }},
      "dependencies": [],
      "status": "pending"
    }}
  ]
}}
"""

try:
    p = PLAN_GENERATION_PROMPT.format(
        task_id=1,
        priority=1,
        title="test",
        description="test"
    )
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
