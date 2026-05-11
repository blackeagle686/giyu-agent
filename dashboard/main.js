const API_BASE = 'http://127.0.0.1:8765';
let cpuChart, ramChart, diskChart, netChart, scoreChart;
const historySize = 20;

const charts = {
    cpu: { instance: null, data: Array(historySize).fill(0) },
    ram: { instance: null, data: Array(historySize).fill(0) },
    disk: { instance: null, data: Array(historySize).fill(0) },
    net: { instance: null, data: Array(historySize).fill(0) }
};

let isStreaming = false;

// Colors from style.css
const COLORS = {
    primary: '#00f2ff',
    secondary: '#7000ff',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    ghost: '#475569'
};

function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: {
            x: { display: false },
            y: { display: false, min: 0, max: 100 }
        },
        elements: {
            line: { 
                tension: 0.4, 
                borderWidth: 2, 
                borderColor: COLORS.primary, 
                fill: true, 
                backgroundColor: 'rgba(0, 242, 255, 0.05)' 
            },
            point: { radius: 0 }
        },
        animation: { duration: 1000 }
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

    charts.net.instance = new Chart(document.getElementById('netChart'), {
        type: 'line',
        data: { labels: Array(historySize).fill(''), datasets: [{ data: charts.net.data }] },
        options: commonOptions
    });

    // Score Doughnut Chart
    scoreChart = new Chart(document.getElementById('scoreChart'), {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: [COLORS.primary, 'rgba(255, 255, 255, 0.03)'],
                borderWidth: 0,
                circumference: 270,
                rotation: 225,
                cutout: '85%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { tooltip: { enabled: false } },
            animation: { animateRotate: true, duration: 2000 }
        }
    });
}

function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString([], { hour12: false });
}

let lastDataHash = '';
let localReports = [];

async function updateData() {
    if (isStreaming) return; // Prevent background sync from wiping active chat
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

        const currentHash = JSON.stringify({status, backbone});
        if (currentHash === lastDataHash) return;
        lastDataHash = currentHash;

        updateStabilityUI(status.current_report);
        updateMetrics(status.current_report);
        updateHeartbeat(status.agent_heartbeats);
        updateTasks(backbone.tasks, backbone.plans);
        updateLogs(backbone.stability_reports);
        updateReports(backbone.generations);

    } catch (error) {
        console.warn('Sync failed:', error);
    }
}

function updateStabilityUI(report) {
    const score = Math.round(report.score);
    const scoreEl = document.getElementById('stability-score');
    const stateEl = document.getElementById('stability-state');
    
    scoreEl.textContent = score;
    stateEl.textContent = report.state.toUpperCase();
    document.getElementById('anomaly-count').textContent = report.anomalies?.length || 0;

    scoreChart.data.datasets[0].data = [score, 100 - score];
    let color = COLORS.primary;
    if (score < 50) color = COLORS.danger;
    else if (score < 80) color = COLORS.warning;
    
    scoreChart.data.datasets[0].backgroundColor[0] = color;
    scoreChart.update('none');

    stateEl.style.color = color;
    scoreEl.style.color = color;
}

function updateMetrics(report) {
    const metrics = report.metrics || {};
    const values = {
        cpu: metrics.cpu_usage || 0,
        ram: metrics.ram_usage || 0,
        disk: metrics.disk_usage || 0,
        net: metrics.net_latency || 0
    };

    document.getElementById('cpu-value').textContent = Math.round(values.cpu);
    document.getElementById('ram-value').textContent = Math.round(values.ram);
    document.getElementById('disk-value').textContent = Math.round(values.disk);
    document.getElementById('net-value').textContent = Math.round(values.net);

    updateChart(charts.cpu, values.cpu);
    updateChart(charts.ram, values.ram);
    updateChart(charts.disk, values.disk);
    updateChart(charts.net, values.net);
}

function updateChart(chartObj, newValue) {
    chartObj.data.push(newValue);
    chartObj.data.shift();
    chartObj.instance.update('none');
}

function updateHeartbeat(heartbeats) {
    if (!heartbeats) return;
    const grid = document.getElementById('heartbeat-grid');
    const fragment = document.createDocumentFragment();
    
    Object.entries(heartbeats).forEach(([name, status]) => {
        const node = document.createElement('div');
        node.className = `agent-dot ${status === 'active' ? '' : 'missing'}`;
        node.innerHTML = `
            <div class="dot"></div>
            <span>${name}</span>
        `;
        fragment.appendChild(node);
    });
    grid.innerHTML = '';
    grid.appendChild(fragment);
}

function updateTasks(tasks, plans) {
    const list = document.getElementById('task-list');
    if (!tasks || tasks.length === 0) return;

    const fragment = document.createDocumentFragment();
    tasks.forEach(task => {
        const taskEl = document.createElement('div');
        taskEl.className = `step ${task.status === 'in_progress' ? 'active' : (task.status === 'done' ? 'done' : '')}`;
        
        let planHtml = '';
        const taskPlans = (plans || []).filter(p => p.task_id === task.id);
        if (taskPlans.length > 0) {
            planHtml = `<div style="margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.25rem;">` + 
                taskPlans.map(p => `
                    <div style="font-size: 0.65rem; color: ${p.status === 'done' ? COLORS.success : (p.status === 'active' ? COLORS.primary : COLORS.ghost)}">
                        <i class="bi ${p.status === 'done' ? 'bi-check-circle-fill' : 'bi-circle'} me-1"></i> ${p.solution?.approach || p.type}
                    </div>
                `).join('') + `</div>`;
        }

        taskEl.innerHTML = `
            <div>
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
    if (!reports) return;

    const existingCount = terminal.children.length;
    reports.slice(existingCount).forEach(report => {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        const time = new Date(report.timestamp * 1000).toLocaleTimeString([], { hour12: false });
        let levelClass = 'terminal-info';
        if (report.score < 50) levelClass = 'terminal-error';
        else if (report.score < 80) levelClass = 'terminal-warn';

        line.innerHTML = `
            <span class="terminal-time">[${time}]</span>
            <span class="${levelClass}">${report.state.toUpperCase()}: Stability Score ${Math.round(report.score)}</span>
        `;
        terminal.appendChild(line);
    });

    if (reports.length > existingCount) {
        terminal.scrollTop = terminal.scrollHeight;
    }
}

function updateReports(generations) {
    if (!window.marked) return;
    const list = document.getElementById('reports-list');
    const modalHistory = document.getElementById('modal-chat-history');
    
    // Sort combined reports by timestamp (oldest first)
    const combined = [...localReports, ...(generations || [])]
        .sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
    
    if (combined.length === 0) {
        list.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-ghost); font-size: 0.8rem;">Waiting for analysis reports...</div>';
        return;
    }

    // Bento Grid: Newest first
    const bentoReports = [...combined].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    const fragment = document.createDocumentFragment();
    bentoReports.forEach((gen, index) => {
        const item = document.createElement('div');
        item.className = 'report-card';
        // ... (render logic remains same)
        
        let content = '';
        const timestamp = gen.timestamp ? new Date(gen.timestamp * 1000).toLocaleString() : `Report #${index + 1}`;

        if (typeof gen === 'string') content = gen;
        else if (gen.artifacts) {
            content = `### Logic Generation\n\n`;
            gen.artifacts.forEach(art => {
                if (art.type === 'file_write') content += `**File:** \`${art.path}\`\n\`\`\`${art.language}\n${art.code}\n\`\`\`\n\n`;
                else if (art.type === 'terminal') content += `**Command:**\n\`\`\`bash\n${art.code}\n\`\`\`\n\n`;
            });
        } else content = gen.text || gen.content || JSON.stringify(gen, null, 2);

        const innerHtml = `
            <h5><i class="bi bi-shield-shaded"></i> Guardian Report <span style="margin-left: auto; font-size: 0.6rem; color: var(--text-ghost);">${timestamp}</span></h5>
            <div style="font-size: 0.75rem; line-height: 1.6; color: var(--text-dim);">${marked.parse(content)}</div>
        `;
        
        item.innerHTML = innerHtml;
        fragment.appendChild(item);

        // Mirror to modal as Chat Bubbles
        if (modalHistory) {
            const aiMsg = document.createElement('div');
            aiMsg.className = 'message msg-ai';
            
            // If it's a history item that contains both query and analysis
            if (typeof gen === 'object' && gen.content && gen.content.includes('**Query:**')) {
                const parts = gen.content.split('**Analysis:**');
                const userText = parts[0].replace('**Query:**', '').trim();
                const aiText = parts[1].trim();

                const userMsg = document.createElement('div');
                userMsg.className = 'message msg-user';
                userMsg.innerHTML = `<h5>You</h5><div>${userText}</div>`;
                modalFragment.appendChild(userMsg);

                aiMsg.innerHTML = `<h5>Giyu</h5><div>${marked.parse(aiText)}</div>`;
            } else {
                aiMsg.innerHTML = `<h5>Giyu</h5><div>${marked.parse(content)}</div>`;
            }
            modalFragment.appendChild(aiMsg);
        }
    });
    
    list.innerHTML = '';
    list.appendChild(fragment);

    if (modalHistory) {
        modalHistory.innerHTML = '';
        modalHistory.appendChild(modalFragment);
        modalHistory.scrollTop = modalHistory.scrollHeight;
    }
}

async function sendCommand(inputId = 'agent-input') {
    if (isStreaming) return;
    const input = document.getElementById(inputId);
    const task = input.value.trim();
    if (!task) return;

    input.value = '';
    const session_id = 'gui_' + Date.now();
    isStreaming = true;

    // Show user message in modal immediately
    const modalHistory = document.getElementById('modal-chat-history');
    if (modalHistory) {
        if (modalHistory.querySelector('.text-center')) modalHistory.innerHTML = '';
        
        const userMsg = document.createElement('div');
        userMsg.className = 'message msg-user';
        userMsg.innerHTML = `<h5>You</h5><div>${task}</div>`;
        modalHistory.appendChild(userMsg);
        
        const typingMsg = document.createElement('div');
        typingMsg.className = 'message msg-ai typing-indicator';
        typingMsg.id = 'typing-' + session_id;
        typingMsg.innerHTML = `<h5>Giyu</h5><div><i class="bi bi-three-dots"></i> Processing...</div>`;
        modalHistory.appendChild(typingMsg);
        
        modalHistory.scrollTop = modalHistory.scrollHeight;
    }

    // Determine mode from the closest container
    const container = input.closest('.input-container-premium');
    const activeModeBtn = container.querySelector('.mode-btn.active');
    const mode = activeModeBtn ? activeModeBtn.dataset.mode : 'auto';
    
    try {
        const response = await fetch(`${API_BASE}/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task, session_id, mode: mode })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let agentResponse = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const lines = decoder.decode(value).split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const eventString = line.substring(6).trim();
                    if (!eventString) continue;
                    
                    const event = JSON.parse(eventString);
                    if (event.type === 'chunk') {
                        agentResponse += event.content;
                        const typing = document.getElementById('typing-' + session_id);
                        if (typing) typing.remove();
                        
                        // Update/Create AI bubble in real-time
                        let aiBubble = document.getElementById('ai-' + session_id);
                        if (!aiBubble) {
                            aiBubble = document.createElement('div');
                            aiBubble.className = 'message msg-ai';
                            aiBubble.id = 'ai-' + session_id;
                            aiBubble.innerHTML = `<h5>Giyu</h5><div class="content"></div>`;
                            modalHistory.appendChild(aiBubble);
                        }
                        aiBubble.querySelector('.content').innerHTML = marked.parse(agentResponse);
                        modalHistory.scrollTop = modalHistory.scrollHeight;

                    } else if (event.type === 'done') {
                        if (agentResponse.trim()) {
                            localReports.push({
                                timestamp: Date.now() / 1000,
                                content: `**Query:** ${task}\n\n**Analysis:**\n${agentResponse.trim()}`
                            });
                        }
                    }
                }
            }
        }
    } catch (err) {
        console.error('Chat error:', err);
    } finally {
        isStreaming = false;
        const typing = document.getElementById('typing-' + session_id);
        if (typing) typing.remove();
        updateData(); // Final sync
    }
}

function initDashboard() {
    initCharts();
    initNet();
    setInterval(updateClock, 1000);
    setInterval(updateData, 3000);
    
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.addEventListener('click', () => sendCommand('agent-input'));
    }
    
    const agentInput = document.getElementById('agent-input');
    if (agentInput) {
        agentInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendCommand('agent-input');
        });
    }

    const modalSendBtn = document.getElementById('modal-send-btn');
    if (modalSendBtn) {
        modalSendBtn.addEventListener('click', () => sendCommand('modal-agent-input'));
    }
    
    const modalAgentInput = document.getElementById('modal-agent-input');
    if (modalAgentInput) {
        modalAgentInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendCommand('modal-agent-input');
        });
    }

    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const parent = btn.closest('.mode-selector');
            parent.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    updateClock();
    updateData();
}

function initNet() {
    const canvas = document.getElementById('bg-net');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
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
            ctx.fillStyle = COLORS.primary;
            ctx.beginPath();
            ctx.arc(this.x, this.y, 1, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach((p, i) => {
            p.update();
            p.draw();
            for (let j = i + 1; j < particles.length; j++) {
                const dx = p.x - particles[j].x;
                const dy = p.y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.strokeStyle = `rgba(0, 242, 255, ${0.1 * (1 - dist/150)})`;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        });
        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    resize();
    for (let i = 0; i < 60; i++) particles.push(new Particle());
    animate();
}

document.addEventListener('DOMContentLoaded', initDashboard);
