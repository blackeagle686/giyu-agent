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

// Global State Cache
let lastDataHash = '';

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
            return;
        }

        const statusRes = await fetch(`${API_BASE}/stability/status`);
        const status = await statusRes.json();
        const backboneRes = await fetch(`${API_BASE}/stability/backbone`);
        const backbone = await backboneRes.json();

        // Simple Hash Check to avoid unnecessary DOM updates
        const currentHash = JSON.stringify({status, backbone});
        if (currentHash === lastDataHash) return;
        lastDataHash = currentHash;

        updateStabilityUI(status.current_report, status.escalation_state);
        updateMetrics(status.current_report);
        updateHeartbeat(status.agent_heartbeats);
        updateTasks(backbone.tasks, backbone.plans, backbone.execution_state);
        updateLogs(backbone.stability_reports);
        updateReports(backbone.generations);

    } catch (error) {
        console.error('Failed to fetch status:', error);
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
    scoreChart.update('none');

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
    
    const cpu = report.metrics?.cpu_usage || 0;
    const ram = report.metrics?.ram_usage || 0;
    const disk = report.metrics?.disk_usage || 0;

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
    if (!heartbeats) return;
    const grid = document.getElementById('heartbeat-grid');
    
    // Only rebuild if the number of agents or their names changed
    // or use a hash to check for status changes
    const currentHash = JSON.stringify(heartbeats);
    if (grid.dataset.hash === currentHash) return;
    grid.dataset.hash = currentHash;

    const fragment = document.createDocumentFragment();
    for (const [name, status] of Object.entries(heartbeats)) {
        const node = document.createElement('div');
        node.className = `agent-node ${status === 'active' ? '' : 'missing'}`;
        node.innerHTML = `
            <div class="status-icon">${status === 'active' ? '✓' : '✗'}</div>
            <span>${name}</span>
        `;
        fragment.appendChild(node);
    }
    grid.innerHTML = '';
    grid.appendChild(fragment);
}

function updateTasks(tasks, plans, state) {
    const list = document.getElementById('task-list');
    
    if (!tasks || tasks.length === 0) {
        if (list.innerHTML !== '') list.innerHTML = '<p style="font-size: 0.8rem; color: var(--text-dim)">Waiting for tasks...</p>';
        return;
    }

    const fragment = document.createDocumentFragment();
    tasks.forEach(task => {
        const taskEl = document.createElement('div');
        taskEl.className = `step ${task.status === 'in_progress' ? 'active' : (task.status === 'done' ? 'done' : '')}`;
        
        let planHtml = '';
        const taskPlans = (plans || []).filter(p => p.task_id === task.id);
        
        if (taskPlans.length > 0) {
            planHtml = `<div class="sub-steps">` + 
                taskPlans.map(p => `
                    <div class="sub-step ${p.status === 'done' ? 'done' : (p.status === 'active' ? 'active' : '')}">
                        <span class="sub-icon">${p.status === 'done' ? '✓' : '○'}</span>
                        <span class="sub-text">${p.solution?.approach || p.type}</span>
                    </div>
                `).join('') + 
                `</div>`;
        }

        taskEl.innerHTML = `
            <div class="step-content">
                <h4>${task.title}</h4>
                <p>${task.description || ''}</p>
                ${planHtml}
            </div>
        `;
        fragment.appendChild(taskEl);
    });
    list.innerHTML = '';
    list.appendChild(fragment);
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
    });

    // Cap logs at 50 lines for performance
    while (terminal.children.length > 50) {
        terminal.removeChild(terminal.firstChild);
    }
    
    if (reports.length > existingCount) {
        terminal.scrollTop = terminal.scrollHeight;
    }
}

function updateReports(generations) {
    if (!generations) return;
    const list = document.getElementById('reports-list');
    
    const currentHash = JSON.stringify(generations);
    if (list.dataset.hash === currentHash) return;
    list.dataset.hash = currentHash;

    if (generations.length === 0) {
        list.innerHTML = '<p style="font-size: 0.8rem; color: var(--text-dim); padding: 1rem;">No reports generated yet.</p>';
        return;
    }

    const fragment = document.createDocumentFragment();
    generations.forEach((gen, index) => {
        const item = document.createElement('div');
        item.className = 'report-item';
        
        // Generations might be simple strings or objects
        const content = typeof gen === 'string' ? gen : (gen.text || gen.content || JSON.stringify(gen));
        const timestamp = gen.timestamp ? new Date(gen.timestamp * 1000).toLocaleString() : `Report #${index + 1}`;

        item.innerHTML = `
            <div class="report-header">
                <span>ANALYSIS REPORT</span>
                <span>${timestamp}</span>
            </div>
            <div class="report-content">${content}</div>
        `;
        fragment.appendChild(item);
    });
    
    list.innerHTML = '';
    list.appendChild(fragment);
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
    initNet(); // Start the background net
    setInterval(updateClock, 1000);
    setInterval(updateData, 3000);
    
    document.getElementById('send-btn').addEventListener('click', sendCommand);
    document.getElementById('agent-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendCommand();
    });

    updateClock();
    updateData();
});

// Interactive Net Background
function initNet() {
    const canvas = document.getElementById('bg-net');
    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouse = { x: null, y: null };

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.x;
        mouse.y = e.y;
    });

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        draw() {
            ctx.fillStyle = '#64ffda';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function init() {
        particles = [];
        for (let i = 0; i < 80; i++) {
            particles.push(new Particle());
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            
            for (let j = i; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 150) {
                    ctx.strokeStyle = `rgba(100, 255, 218, ${1 - distance/150})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    resize();
    init();
    animate();
}
