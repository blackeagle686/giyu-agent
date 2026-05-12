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
    async def execute(self, log_path: str = None, lines: int = 100, **kwargs) -> ToolResult:
        try:
            is_windows = os.name == "nt"
            
            if is_windows:
                # Windows Event Log fallback
                cmd = f'powershell "Get-EventLog -LogName System -Newest {lines} | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json"'
                result = subprocess.check_output(cmd, shell=True).decode()
                return ToolResult(success=True, output=result)
            
            # Linux logic
            if log_path is None:
                log_path = "/var/log/syslog"
                
            if not os.path.exists(log_path):
                result = subprocess.check_output(f"dmesg | tail -n {lines}", shell=True).decode()
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
        # Use relative path or home-based path that works on both OS
        base_path = os.path.expanduser("~/.giyu/hashira")
        for agent in agents:
            path = os.path.join(base_path, agent)
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
            cmd = ["git", "log", "-n", "5", "--oneline"]
            result = subprocess.check_output(cmd, cwd=repo_path, stderr=subprocess.STDOUT).decode()
            return ToolResult(success=True, output=f"Recommended Rollback Points:\n{result}")
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Git lookup failed: {str(e)}")

class CoreEscalationTrigger(BaseTool):
    name = "core_escalation_trigger"
    description = "Sends critical alerts to Core Orchestrator when system is unstable."
    async def execute(self, level: str, message: str, **kwargs) -> ToolResult:
        alert = f"[ESCALATION] Level: {level}, Message: {message}, Time: {time.time()}"
        alert_file = os.path.expanduser("~/.giyu/alerts.log")
        os.makedirs(os.path.dirname(alert_file), exist_ok=True)
        with open(alert_file, "a") as f:
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
