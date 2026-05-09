import psutil
import os
import time
import subprocess
import asyncio
from typing import List, Dict, Any
from phoenix.framework.agent.tools.base import BaseTool, ToolResult
from giyu.runtime.pty_executor import PTYExecutor
from giyu.cognition.brains.command_translator import CommandRuleEngine

class SystemSnapshotReader(BaseTool):
    name = "system_snapshot_reader"
    description = "Reads current CPU, RAM, disk, and process state."
    async def execute(self, **kwargs) -> ToolResult:
        try:
            snapshot = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "ram_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "process_count": len(psutil.pids()),
                "timestamp": time.time()
            }
            return ToolResult(success=True, output=str(snapshot))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class LogStreamAnalyzer(BaseTool):
    name = "log_stream_analyzer"
    description = "Parses system logs and extracts errors, warnings, and patterns."
    async def execute(self, log_path: str = "/var/log/syslog", lines: int = 100, **kwargs) -> ToolResult:
        try:
            if not os.path.exists(log_path):
                # Fallback if syslog not accessible
                result = subprocess.check_output(
                    f"dmesg | tail -n {int(lines)}",
                    shell=True,
                    text=True,
                )
                return ToolResult(success=True, output=result)
            
            result = subprocess.check_output(["tail", f"-n {lines}", log_path]).decode()
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class AgentHeartbeatMonitor(BaseTool):
    name = "agent_heartbeat_monitor"
    description = "Checks health status and responsiveness of all agents."
    async def execute(self, **kwargs) -> ToolResult:
        agents = ["Giyu", "Shinobu", "Rengoku", "Mitsuri", "Obanai", "Sanemi", "Gyomei", "Tengen", "Muichiro"]
        status = {}
        base_dir = os.getenv("HASHIRA_ROOT", "/home/tlk/Documents/Projects/my_AItools/Hashira")
        for agent in agents:
            path = os.path.join(base_dir, agent)
            status[agent] = "active" if os.path.exists(path) else "missing"
        return ToolResult(success=True, output=str(status))

class AnomalyDetector(BaseTool):
    name = "anomaly_detector"
    description = "Detects abnormal spikes or deviations in system metrics."
    async def execute(self, metric_name: str, value: float, threshold: float = 80.0, **kwargs) -> ToolResult:
        is_anomaly = value > threshold
        return ToolResult(success=True, output=f"Metric: {metric_name}, Value: {value}, Anomaly: {is_anomaly}")

class StabilityScoreCalculator(BaseTool):
    name = "stability_score_calculator"
    description = "Computes overall system stability score (0–100)."
    async def execute(self, cpu: float, ram: float, disk: float, **kwargs) -> ToolResult:
        from ..cognition.brains.stability_scorer import StabilityScorer
        scorer = StabilityScorer()
        result = scorer.compute_score({"cpu_usage": cpu, "ram_usage": ram, "disk_usage": disk})
        return ToolResult(success=True, output=str(result))

class ProcessStateTracker(BaseTool):
    name = "process_state_tracker"
    description = "Tracks lifecycle state of running processes."
    async def execute(self, proc_name: str = None, **kwargs) -> ToolResult:
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            if proc_name and proc_name.lower() not in proc.info['name'].lower():
                continue
            procs.append(proc.info)
        return ToolResult(success=True, output=str(procs[:20])) # Limit output

class RollbackRecommendationEngine(BaseTool):
    name = "rollback_recommendation_engine"
    description = "Suggests safe rollback points based on system state history."
    async def execute(self, repo_path: str = ".", **kwargs) -> ToolResult:
        try:
            # Check git log for recent commits
            log = subprocess.check_output(["git", "log", "-n 5", "--oneline"], cwd=repo_path).decode()
            return ToolResult(success=True, output=f"Recommended Rollback Points:\n{log}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class CoreEscalationTrigger(BaseTool):
    name = "core_escalation_trigger"
    description = "Sends critical alerts to Core Orchestrator when system is unstable."
    async def execute(self, level: str, message: str, **kwargs) -> ToolResult:
        alert = f"[ESCALATION] Level: {level}, Message: {message}, Time: {time.time()}"
        alerts_path = os.getenv("GIYU_ALERTS_PATH", "/tmp/hashira_alerts.log")
        with open(alerts_path, "a", encoding="utf-8") as f:
            f.write(alert + "\n")
        return ToolResult(success=True, output=f"Escalated to Core: {alert}")

class ResourcePressureMonitor(BaseTool):
    name = "resource_pressure_monitor"
    description = "Detects CPU/RAM/Disk overload situations."
    async def execute(self, **kwargs) -> ToolResult:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        pressures = []
        if cpu > 80: pressures.append("High CPU Pressure")
        if ram > 80: pressures.append("High RAM Pressure")
        return ToolResult(success=True, output=str(pressures) if pressures else "No pressure detected")

class EventCorrelationTracker(BaseTool):
    name = "event_correlation_tracker"
    description = "Connects multiple system events to identify root cause chains."
    async def execute(self, events: List[str], **kwargs) -> ToolResult:
        # This would ideally call the CorrelationEngine brain, but as a tool it just returns the input for now
        return ToolResult(success=True, output=f"Tracking correlation for {len(events)} events: {events}")

class ShellCommandTool(BaseTool):
    name = "run_shell_command"
    description = "Safely executes system commands for diagnostics (e.g., 'ip addr', 'ping -c 1 8.8.8.8', 'netstat')."
    async def execute(self, command: str, **kwargs) -> ToolResult:
        try:
            rule_engine = CommandRuleEngine()
            cmd = (command or "").strip()
            if not cmd:
                return ToolResult(success=False, output="", error="Empty command rejected.")
            if rule_engine.is_blocked(cmd):
                return ToolResult(success=False, output="", error="Command rejected by blocklist.")
            lowered = cmd.lower()
            high_risk_substrings = [
                "rm ", "rmdir ", "unlink ", "truncate ", "mkfs", "dd ", "fdisk", "parted",
                "reboot", "shutdown", "halt", "stress", "stress-ng", "gpu-burn",
                "yes ", ":(){ :|:& };:", "while true", "for (;;)", "cryptominer",
            ]
            for pat in high_risk_substrings:
                if pat in lowered:
                    return ToolResult(success=False, output="", error=f"Command rejected by safety policy: {pat}")

            timeout_ms = int(kwargs.get("timeout_ms", 30000))
            working_dir = kwargs.get("working_dir") or os.getenv("GIYU_WORKDIR", "/tmp/giyu")
            env_vars = kwargs.get("env_vars") or {}

            executor = PTYExecutor()
            result = await executor.execute(
                command=cmd,
                working_dir=working_dir,
                env_vars=env_vars,
                timeout_ms=timeout_ms,
            )
            if result["exit_code"] != 0:
                return ToolResult(success=False, output=result["output"], error=f"Exit code {result['exit_code']}")
            return ToolResult(success=True, output=result["output"])
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ProcessAnomalyMonitor:
    """Tracks process anomalies for process trees owned by Giyu."""

    def __init__(self):
        self._cpu_breach: dict[int, int] = {}
        self._rss_history: dict[int, tuple[float, float]] = {}

    def evaluate_process(self, proc: psutil.Process) -> dict | None:
        try:
            now = time.time()
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_info().rss
            pid = proc.pid
            if proc.status() == psutil.STATUS_ZOMBIE:
                return {"pid": pid, "anomaly_type": "zombie", "action_taken": "waitpid_cleanup"}
            if cpu > 90.0:
                self._cpu_breach[pid] = self._cpu_breach.get(pid, 0) + 1
                if self._cpu_breach[pid] >= 10:
                    return {"pid": pid, "cpu_pct": cpu, "anomaly_type": "cpu_runaway", "action_taken": "warn_or_kill"}
            else:
                self._cpu_breach[pid] = 0

            prev = self._rss_history.get(pid)
            self._rss_history[pid] = (now, float(mem))
            if prev:
                prev_ts, prev_mem = prev
                dt = max(now - prev_ts, 1e-6)
                growth_mb_per_min = ((mem - prev_mem) / (1024 * 1024)) / (dt / 60)
                if growth_mb_per_min > 50:
                    return {
                        "pid": pid,
                        "mem_rss": mem,
                        "anomaly_type": "memory_growth",
                        "growth_mb_per_min": round(growth_mb_per_min, 2),
                        "action_taken": "warn_or_kill",
                    }
        except Exception:
            return None
        return None

class SystemSecurityAuditor(BaseTool):
    name = "security_audit_tool"
    description = "Performs a comprehensive security audit of the system and network (ports, logins, firewall, active connections, DNS, and processes)."
    async def execute(self, **kwargs) -> ToolResult:
        report = []
        try:
            # 1. System Info & Uptime
            report.append("### 🖥️ SYSTEM CORE STATUS")
            uname = subprocess.check_output("uname -a", shell=True).decode().strip()
            uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
            report.append(f"- **Kernel:** `{uname}`\n- **Uptime:** `{uptime}`")

            # 2. Network Security (Ports & Connections)
            report.append("\n### 🌐 NETWORK SECURITY AUDIT")
            ports = subprocess.check_output("ss -tuln | head -n 15", shell=True).decode().strip()
            report.append("#### Listening Ports (IPv4/IPv6):\n```text\n" + ports + "\n```")
            
            connections = subprocess.check_output("ss -atn | head -n 10", shell=True).decode().strip()
            report.append("#### Established Connections (Top 10):\n```text\n" + connections + "\n```")

            dns = subprocess.check_output("cat /etc/resolv.conf | grep nameserver", shell=True).decode().strip()
            report.append(f"#### DNS Configuration:\n`{dns}`")

            # 3. Access & Privilege Audit
            report.append("\n### 🔑 ACCESS & PRIVILEGE AUDIT")
            logins = subprocess.check_output("last -n 10", shell=True).decode().strip()
            report.append("#### Recent Login Activity:\n```text\n" + logins + "\n```")
            
            # Check for failed login attempts if possible
            try:
                failed = subprocess.check_output("grep 'Failed password' /var/log/auth.log | tail -n 5 2>/dev/null || echo 'Insufficient permissions to read auth logs'", shell=True).decode().strip()
                if failed: report.append(f"#### Detected Login Failures:\n```text\n{failed}\n```")
            except: pass

            # 4. Firewall & Perimeter
            report.append("\n### 🛡️ FIREWALL & PERIMETER")
            try:
                ufw = subprocess.check_output("sudo ufw status 2>/dev/null || echo 'UFW not available or requires sudo'", shell=True).decode().strip()
                report.append(f"**UFW Status:** `{ufw}`")
            except:
                report.append("**Firewall Status:** `Could not determine (check permissions)`")

            # 5. Critical Process Audit
            report.append("\n### ⚙️ CRITICAL PROCESS AUDIT")
            root_procs = subprocess.check_output("ps -U root -u root u | head -n 10", shell=True).decode().strip()
            report.append("#### Top Root Processes:\n```text\n" + root_procs + "\n```")

            output = "\n".join(report)
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Comprehensive audit failed: {str(e)}")
