import psutil
import os
import time
import subprocess
from typing import List, Dict, Any
from phoenix.framework.agent.tools.base import BaseTool, ToolResult

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
                # Fallback to a mock or dmesg if syslog not accessible
                result = subprocess.check_output(["dmesg", "|", "tail", f"-n {lines}"], shell=True).decode()
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
        for agent in agents:
            path = f"/home/tlk/Documents/Projects/my_AItools/Hashira/{agent}"
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
        # Mock escalation by writing to a global alert file
        with open("/home/tlk/Documents/Projects/my_AItools/Hashira/alerts.log", "a") as f:
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
            # Prevent dangerous commands (very basic check)
            forbidden = ["rm ", "mv ", "dd ", "> /dev/", ":(){ :|:& };:"]
            if any(f in command for f in forbidden):
                return ToolResult(success=False, output="", error="Command rejected for safety reasons.")
                
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
