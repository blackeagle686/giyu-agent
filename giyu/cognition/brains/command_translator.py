import os
import re
import json
from typing import Any, Dict, Optional


class CommandRuleEngine:
    """Deny-by-default rule engine with optional LLM fallback."""

    def __init__(self, rules_path: Optional[str] = None):
        self.rules_path = rules_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "helpers",
            "command_rules.yaml",
        )
        self.allow_rules: list[dict[str, str]] = []
        self.allow_command_patterns: list[str] = []
        self.block_patterns: list[str] = []
        self._load_rules()

    def _load_rules(self) -> None:
        text = ""
        if os.path.exists(self.rules_path):
            with open(self.rules_path, "r", encoding="utf-8") as f:
                text = f.read()
        if not text.strip():
            self.allow_rules = []
            self.allow_command_patterns = []
            self.block_patterns = []
            return

        try:
            import yaml  # type: ignore
            raw = yaml.safe_load(text) or {}
        except Exception:
            # Fallback parser for very simple YAML-like content.
            raw = {"allow_rules": [], "allow_command_patterns": [], "block_patterns": []}
            current_rule = None
            in_allow = False
            in_allow_cmd = False
            in_block = False
            for line in text.splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.startswith("allow_rules:"):
                    in_allow, in_allow_cmd, in_block = True, False, False
                    continue
                if s.startswith("allow_command_patterns:"):
                    in_allow, in_allow_cmd, in_block = False, True, False
                    continue
                if s.startswith("block_patterns:"):
                    in_allow, in_allow_cmd, in_block = False, False, True
                    continue
                if in_allow and s.startswith("- name:"):
                    if current_rule:
                        raw["allow_rules"].append(current_rule)
                    current_rule = {"name": s.split(":", 1)[1].strip()}
                    continue
                if in_allow and ":" in s and current_rule is not None:
                    k, v = s.split(":", 1)
                    current_rule[k.strip()] = v.strip().strip('"').strip("'")
                    continue
                if in_allow_cmd and s.startswith("- "):
                    raw["allow_command_patterns"].append(
                        s[2:].strip().strip('"').strip("'")
                    )
                    continue
                if in_block and s.startswith("- "):
                    raw["block_patterns"].append(s[2:].strip().strip('"').strip("'"))
            if current_rule:
                raw["allow_rules"].append(current_rule)

        self.allow_rules = raw.get("allow_rules", []) or []
        self.allow_command_patterns = raw.get("allow_command_patterns", []) or []
        self.block_patterns = raw.get("block_patterns", []) or []

    def is_blocked(self, command: str) -> bool:
        cmd = command.strip()
        for pat in self.block_patterns:
            if re.search(pat, cmd, flags=re.IGNORECASE):
                return True
        return False

    def match_intent(self, intent: str, working_dir: str = ".") -> Dict[str, Any]:
        raw_intent = (intent or "").strip()
        for rule in self.allow_rules:
            pattern = rule.get("intent_regex", "")
            if pattern and re.search(pattern, raw_intent, flags=re.IGNORECASE):
                cmd = (rule.get("command_template", "") or "").format(working_dir=working_dir)
                return {
                    "status": "allow_match",
                    "rule_name": rule.get("name", "unnamed_rule"),
                    "command": cmd,
                }
        return {"status": "no_match", "command": None}

    def is_command_allowed(self, command: str) -> bool:
        cmd = (command or "").strip()
        if not cmd:
            return False
        for pat in self.allow_command_patterns:
            if re.search(pat, cmd, flags=re.IGNORECASE):
                return True
        return False


class LLMCommandTranslator:
    """Translate ambiguous intent into one safe command."""

    def __init__(self, llm):
        self.llm = llm

    async def translate(self, intent: str, working_dir: str = ".") -> Dict[str, Any]:
        prompt = (
            "You are a deterministic shell command translator.\n"
            "Convert the intent into a single safe Linux command.\n"
            "Return strict JSON only with fields:\n"
            '{"command":"...", "reason":"...", "confidence":0.0}\n'
            "Rules:\n"
            "- One command only\n"
            "- No pipes to shell interpreters (bash/sh)\n"
            "- No destructive commands\n"
            f"- Working directory is: {working_dir}\n"
            f"Intent: {intent}\n"
        )
        raw = await self.llm.generate(prompt, max_tokens=180)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            payload = json.loads(raw[start : end + 1])
        except Exception:
            payload = {"command": "", "reason": "Invalid translator output", "confidence": 0.0}
        return payload
