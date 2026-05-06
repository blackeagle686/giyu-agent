# 🌊 Giyu: Full Capabilities List

Here is everything Giyu can do as the Hashira-OS Stability Guardian:

### 🛡️ Monitoring & Diagnostics
- **Monitor CPU Usage**: Capture real-time processor load percentage.
- **Track Memory Utilization**: Observe RAM consumption and identify leaks.
- **Read Disk I/O & Usage**: Monitor storage health and remaining capacity.
- **Calculate Stability Score**: Generate a 0–100 health rating for the system.
- **Detect Resource Pressure**: Identify when hardware reaches critical stress levels.
- **Track Process States**: Monitor lifecycle and resource usage of active processes.

### 🔍 Analysis & Root Cause
- **Analyze System Logs**: Parse `/var/log/syslog` and `dmesg` for critical errors.
- **Detect Anomalies**: Spot statistical deviations from normal system behavior.
- **Correlate System Events**: Connect multiple logs into a causal chain to find root causes.
- **Identify Service Crashes**: Detect when system services fail or hang.

### 👥 Agent Coordination
- **Monitor Agent Heartbeats**: Verify if other Hashira agents are responsive.
- **Track Environment Presence**: Identify missing or inactive agent folders.
- **Update Agent Health Grid**: Maintain a real-time status view of all agents.

### 🚀 Escalation & Recovery
- **Apply Decision Rules**: Categorize system state into `Ignore`, `Warn`, or `Escalate`.
- **Trigger Core Alerts**: Proactively notify the orchestrator of critical instabilities.
- **Recommend Rollbacks**: Analyze Git history to find safe recovery points.
- **Propose Actions**: Suggest specific diagnostic commands based on identified issues.

### 🖥️ Dashboard Interaction
- **Visualize Metrics**: Stream live line charts for CPU, RAM, and Disk health.
- **Show Task Steppers**: Display real-time thinking and planning steps for AI tasks.
- **Live Gauge Updates**: Provide a pulsing, visual representation of system health.
- **Issue Direct Commands**: Execute diagnostic prompts directly from the web GUI.
- **Stream Agent Output**: View real-time log analysis and results via SSE.
