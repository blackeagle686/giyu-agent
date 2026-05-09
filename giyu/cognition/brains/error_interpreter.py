import json


class ErrorInterpreter:
    """Structured non-zero exit error interpretation."""

    def __init__(self, llm):
        self.llm = llm

    async def interpret(self, command: str, stderr: str, exit_code: int) -> dict:
        prompt = (
            "You are a deterministic Linux error classifier.\n"
            "Return JSON only with keys:\n"
            '{"error_class":"...", "likely_cause":"...", "suggested_fix":"...", "is_retryable":true}\n'
            f"Command: {command}\n"
            f"ExitCode: {exit_code}\n"
            f"Stderr: {stderr[:2000]}\n"
        )
        raw = await self.llm.generate(prompt, max_tokens=220)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            data = json.loads(raw[start : end + 1])
        except Exception:
            data = {
                "error_class": "unknown_error",
                "likely_cause": "Unable to parse model output.",
                "suggested_fix": "Check stderr and retry with corrected inputs.",
                "is_retryable": False,
            }
        return data
