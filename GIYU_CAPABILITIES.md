# 🌊 Giyu: System Stability Guardian

Giyu is a high-fidelity **System Stability Agent** within the Hashira-OS environment. Designed with a hybrid cognitive architecture, he combines deterministic system analysis with deep LLM-powered reasoning to ensure your environment remains in a state of "Tranquility."

## 🧠 Core Capabilities

### 1. Real-Time Stability Monitoring
Giyu constantly observes the system's pulse using specialized diagnostic tools:
- **System Snapshot**: Captures real-time CPU, RAM, and Disk utilization percentages.
- **Stability Scoring**: Calculates a deterministic health score (0–100) based on resource pressure and anomaly detection.
- **Resource Pressure Detection**: Automatically identifies when the system is nearing critical thresholds.

### 2. Deep Log Analysis
Giyu can parse vast amounts of system logs to identify patterns that lead to instability:
- **Log Stream Analysis**: Scans `/var/log/syslog` or `dmesg` for critical errors, kernel panics, or service crashes.
- **Anomaly Detection**: Uses statistical deviations to spot abnormal behavior before it causes a crash.
- **Event Correlation**: Connects seemingly unrelated log events into a "causal chain" to find the root cause of an issue.

### 3. Multi-Agent Oversight
In the Hashira-OS ecosystem, Giyu acts as the guardian for other agents:
- **Heartbeat Monitoring**: Periodically checks if other agents (Shinobu, Rengoku, etc.) are responsive and active.
- **Health Grid**: Visualizes the status of all available agents in a unified dashboard.

### 4. Automated Escalation & Recovery
When the system state degrades, Giyu transitions from "Calm" to "Action":
- **Decision Gate**: Categorizes stability scores into escalation levels (`ignore`, `warn`, `escalate`, `emergency`).
- **Rollback Recommendations**: Analyzes recent git history to suggest safe rollback points if a code change caused the instability.
- **Core Escalation**: Proactively alerts the Core Orchestrator when manual intervention or emergency protocols are required.

---

## 🛠️ Specialized Toolset

| Tool Name | Purpose |
| :--- | :--- |
| `system_snapshot_reader` | Reads hardware metrics (CPU/RAM/Disk). |
| `log_stream_analyzer` | Parses system logs for error patterns. |
| `agent_heartbeat_monitor` | Tracks the health of all Hashira agents. |
| `anomaly_detector` | Identifies spikes or deviations in metrics. |
| `process_state_tracker` | Monitors high-resource or zombie processes. |
| `rollback_recommendation_engine` | Suggests recovery points via Git history. |
| `core_escalation_trigger` | Alerts the central orchestrator of critical failure. |

---

## 🖥️ Web Dashboard
Giyu comes with a premium **System Stability Dashboard** (accessible at `http://localhost:8765/dashboard/`) featuring:
- **Live Gauge Charts**: Real-time visualization of stability scores.
- **Metric Streams**: Dynamic line charts for hardware utilization.
- **Task Stepper**: Live view of Giyu's internal thinking and planning steps.
- **Command Center**: Direct interface to issue diagnostic commands to the agent.

---
*"The flow of the system must remain undisturbed. I will protect its tranquility."* — **Giyu**
