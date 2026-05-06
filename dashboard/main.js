const API_BASE = 'http://127.0.0.1:8765';
let cpuChart, ramChart, diskChart, scoreChart;
const historySize = 20;
const charts = {
    cpu: { instance: null, data: Array(historySize).fill(0) },
    ram: { instance: null, data: Array(historySize).fill(0) },
    disk: { instance: null, data: Array(historySize).fill(0) }
};

// Initialize Charts
function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { display: false },
            y: { display: false, min: 0, max: 100 }
        },
        elements: {
            line: { tension: 0.4, borderWidth: 2, borderColor: '#64ffda', fill: true, backgroundColor: 'rgba(100, 255, 218, 0.1)' },
            point: { radius: 0 }
        }
    };

    charts.cpu.instance = new Chart(document.getElementById('cpuChart'), {
        type: 'line',
        data: { labels: Array(historySize).fill(''), datasets: [{ data: charts.cpu.data }] },
        options: commonOptions
    });

    charts.ram.instance = new Chart(document.getElementById('ramChart'), {
        type: 'line',
        data: { labels: Array(historySize).fill(''), datasets: [{ data: charts.ram.data }] },
        options: commonOptions
    });

    charts.disk.instance = new Chart(document.getElementById('diskChart'), {
        type: 'line',
        data: { labels: Array(historySize).fill(''), datasets: [{ data: charts.disk.data }] },
        options: commonOptions
    });

    // Score Doughnut Chart
    scoreChart = new Chart(document.getElementById('scoreChart'), {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#64ffda', 'rgba(255, 255, 255, 0.05)'],
                borderWidth: 0,
                circumference: 270,
                rotation: 225,
                cutout: '85%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { tooltip: { enabled: false } }
        }
    });
}

// Update Clock
function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString();
}

// Fetch and Update Data
async function updateData() {
    try {
        const healthRes = await fetch(`${API_BASE}/health`);
        const health = await healthRes.json();
        
        const overlay = document.getElementById('loading-overlay');
        if (health.agent_ready) {
            overlay.classList.add('hidden');
        } else {
            overlay.classList.remove('hidden');
            return; // Don't fetch other data if agent not ready
        }

        const response = await fetch(`${API_BASE}/stability/status`);
        const status = await response.json();
        const backboneRes = await fetch(`${API_BASE}/stability/backbone`);
        const backbone = await backboneRes.json();

        updateStabilityUI(status.current_report, status.escalation_state);
        updateMetrics(status.current_report);
        updateHeartbeat(status.agent_heartbeats);
        updateTasks(backbone.tasks, backbone.execution_state);
        updateLogs(backbone.stability_reports);

    } catch (error) {
        console.error('Failed to fetch status:', error);
        document.getElementById('agent-status').textContent = 'OFFLINE';
        document.getElementById('agent-status').style.borderColor = '#f44336';
        document.getElementById('agent-status').style.color = '#f44336';
    }
}

function updateStabilityUI(report, escalation) {
    const score = Math.round(report.score);
    document.getElementById('stability-score').textContent = score;
    document.getElementById('stability-state').textContent = report.state.toUpperCase();
    document.getElementById('anomaly-count').textContent = report.anomalies?.length || 0;

    // Update Doughnut
    scoreChart.data.datasets[0].data = [score, 100 - score];
    let color = '#64ffda';
    if (score < 50) color = '#f44336';
    else if (score < 80) color = '#ffb74d';
    scoreChart.data.datasets[0].backgroundColor[0] = color;
    scoreChart.update();

    document.getElementById('stability-state').style.color = color;
    document.getElementById('stability-score').style.color = color;
}

function updateMetrics(report) {
    const metrics = report.metrics || {
        cpu_usage: Math.random() * 20 + 20, // Fallback random if server doesn't provide
        ram_usage: Math.random() * 10 + 40,
        disk_usage: 15
    };
    
    // Use metrics from report if available (from system_snapshot_reader)
    // The StabilityScorer might return metrics in the report.
    // In our backend implementation, we might need to ensure they are there.
    
    const cpu = report.metrics?.cpu_percent || 0;
    const ram = report.metrics?.ram_percent || 0;
    const disk = report.metrics?.disk_percent || 0;

    document.getElementById('cpu-value').textContent = Math.round(cpu);
    document.getElementById('ram-value').textContent = Math.round(ram);
    document.getElementById('disk-value').textContent = Math.round(disk);

    updateChart(charts.cpu, cpu);
    updateChart(charts.ram, ram);
    updateChart(charts.disk, disk);
}

function updateChart(chartObj, newValue) {
    chartObj.data.push(newValue);
    chartObj.data.shift();
    chartObj.instance.update();
}

function updateHeartbeat(heartbeats) {
    const grid = document.getElementById('heartbeat-grid');
    grid.innerHTML = '';
    
    for (const [name, status] of Object.entries(heartbeats)) {
        const node = document.createElement('div');
        node.className = `agent-node ${status === 'active' ? '' : 'missing'}`;
        node.innerHTML = `
            <div class="status-icon">${status === 'active' ? '✓' : '✗'}</div>
            <span>${name}</span>
        `;
        grid.appendChild(node);
    }
}

function updateTasks(tasks, state) {
    const list = document.getElementById('task-list');
    list.innerHTML = '';
    
    if (!tasks || tasks.length === 0) {
        list.innerHTML = '<p style="font-size: 0.8rem; color: var(--text-dim)">Waiting for tasks...</p>';
        return;
    }

    tasks.forEach(task => {
        const step = document.createElement('div');
        step.className = `step ${task.status === 'in_progress' ? 'active' : (task.status === 'done' ? 'done' : '')}`;
        step.innerHTML = `
            <div class="step-content">
                <h4>${task.title}</h4>
                <p>${task.description || ''}</p>
            </div>
        `;
        list.appendChild(step);
    });
}

function updateLogs(reports) {
    const terminal = document.getElementById('log-terminal');
    const existingCount = terminal.children.length;
    
    if (!reports) return;

    // Only add new reports
    reports.slice(existingCount).forEach(report => {
        const line = document.createElement('div');
        line.className = 'line';
        const time = new Date(report.timestamp * 1000).toLocaleTimeString();
        let levelClass = 'info';
        if (report.score < 50) levelClass = 'error';
        else if (report.score < 80) levelClass = 'warn';

        line.innerHTML = `
            <span class="timestamp">[${time}]</span>
            <span class="${levelClass}">${report.state.toUpperCase()}: Stability Score ${Math.round(report.score)}</span>
        `;
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    });
}

// Send Command
async function sendCommand() {
    const input = document.getElementById('agent-input');
    const task = input.value.trim();
    if (!task) return;

    input.value = '';
    const session_id = 'gui_session_' + Math.floor(Math.random() * 1000);
    
    // Clear terminal and tasks
    document.getElementById('log-terminal').innerHTML = '<div class="line"><span class="info">Sending command to Giyu...</span></div>';
    document.getElementById('task-list').innerHTML = '';

    const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, session_id, mode: 'auto' })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const event = JSON.parse(line.substring(6));
                handleAgentEvent(event);
            }
        }
    }
}

function handleAgentEvent(event) {
    const terminal = document.getElementById('log-terminal');
    const line = document.createElement('div');
    line.className = 'line';

    if (event.type === 'status') {
        line.innerHTML = `<span class="info">STATUS: ${event.content}</span>`;
    } else if (event.type === 'chunk') {
        // Just log the text chunk to the terminal
        line.innerHTML = `<span>${event.content}</span>`;
    } else if (event.type === 'error') {
        line.innerHTML = `<span class="error">ERROR: ${event.content}</span>`;
    } else if (event.type === 'done') {
        line.innerHTML = `<span class="success">✓ COMMAND COMPLETE</span>`;
    }

    if (line.innerHTML) {
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }
    
    // Refresh tasks from backbone frequently during execution
    updateData();
}

// Main Initialization
window.addEventListener('DOMContentLoaded', () => {
    initCharts();
    setInterval(updateClock, 1000);
    setInterval(updateData, 2000);
    
    document.getElementById('send-btn').addEventListener('click', sendCommand);
    document.getElementById('agent-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendCommand();
    });

    updateClock();
    updateData();
});
