<img src="./giyu.png" alt="Giyu Agent" width="100%">

# Giyu Agent 🌊
## The Water Hashira - System Stability Guardian

Giyu is the bedrock of **Hashira-OS**, designed exclusively to ensure operational calmness and system integrity. Unlike general-purpose agents, Giyu is a highly specialized diagnostic sentinel operating on a **Hybrid Cognitive Architecture** that prioritizes precision, deterministic safety, and real-time anomaly detection over open-ended generation.

---

### 🛡️ Role within Hashira-OS
Giyu acts as the autonomous immune system of Hashira-OS. His primary responsibilities include:
1. **Continuous Health Monitoring**: Scanning hardware metrics, agent heartbeats, and process states.
2. **Deterministic Escalation**: Bypassing LLM hallucinations by using strict, rule-based logic to decide when a system warning should become a critical escalation.
3. **Adaptive Context Logging**: Injecting real-time health data (`stability_reports`, `anomalies`, `escalation_state`) directly into the agent network's backbone (`giyu.context.json`), ensuring all other agents are aware of the system's condition.

---

### 🧠 The Hybrid Cognitive Architecture
To achieve absolute reliability, Giyu's cognition is separated into distinct "Brains"—a mix of fast, deterministic rule engines and deep, context-aware LLM evaluators.

#### Deterministic Brains (Fast & Reliable)
*   **`StabilityScorer`**: Calculates a real-time health score (0-100) by weighting immediate hardware metrics (CPU, RAM, Disk). It ensures zero latency and absolute predictability.
*   **`DecisionGate`**: A strict rule engine that maps the `StabilityScorer`'s output to defined action paths (`Ignore`, `Warn`, `Escalate`, `Emergency`). It prevents the LLM from second-guessing critical safety protocols.
*   **`GiyuAnalyzer`**: A heuristic processor that scans log streams and performance metrics to detect spikes, crashes, and resource starvation without the token overhead of an LLM.

#### LLM-Powered Brains (Deep & Contextual)
*   **`GiyuThinker`**: Operates strictly in `STABILITY_MODE`, parsing complex user prompts or raw error signals and decomposing them into rigid, JSON-formatted diagnostic tasks.
*   **`GiyuReflector`**: Analyzes the outcomes of diagnostic actions, categorizing their impact on system integrity (Positive, Neutral, Negative) and storing learnings in long-term memory.
*   **`CorrelationEngine` (Hybrid)**: Fuses heuristic data with LLM reasoning to link disparate system errors (e.g., "A database timeout was caused by a CPU spike from the indexing process") into actionable causal chains.

---

### 🛠️ Custom Stability Toolset
Giyu is equipped with 10 specialized tools specifically engineered for active system monitoring and intervention:

1.  **`system_snapshot_reader`**: Instantly captures OS-level hardware utilization (via `psutil`).
2.  **`agent_heartbeat_monitor`**: Pings and validates the operational status of all other Hashira agents.
3.  **`log_stream_analyzer`**: Tails and filters critical application and system logs for `ERROR` or `FATAL` flags.
4.  **`stability_score_calculator`**: Invokes the `StabilityScorer` to generate an immediate system health grade.
5.  **`anomaly_detector`**: Uses the `GiyuAnalyzer` to detect unusual patterns in active processes.
6.  **`process_state_tracker`**: Ensures mission-critical daemons and services remain active.
7.  **`resource_pressure_monitor`**: Identifies memory leaks, thread starvation, or I/O bottlenecks.
8.  **`event_correlation_tracker`**: Activates the `CorrelationEngine` to map out the root cause of cascading failures.
9.  **`rollback_recommendation_engine`**: Identifies stable system states to revert to in the event of a catastrophic failure.
10. **`core_escalation_trigger`**: Bypasses standard execution to forcefully log and broadcast emergency alerts across the OS.

---

### 📖 How to Run

Ensure that you are using the designated virtual environment to execute the agent.

```bash
# Activate the virtual environment
source phx_venv/bin/activate

# Run the full stability test suite
python Giyu/tests/test_giyu_full.py
```
