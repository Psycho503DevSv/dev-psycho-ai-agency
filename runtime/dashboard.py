import http.server
import socketserver
import json
import os
import threading

from runtime.logger import logger

PORT = 8050

# Variables globales para almacenar el estado y logs de eventos
_state = {
    "status": "IDLE",
    "active_agent": "Ninguno",
    "active_role": "Ninguno",
    "project_name": "Ninguno",
    "workflow_id": "Ninguno",
    "total_calls": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost_usd": 0.0,
    "recent_tool_calls": [],
    "all_steps": [],
    "completed_steps": [],
    "pending_question": None
}

_logs = []
_security_alerts = []

# Bloqueo para evitar colisiones de hilos al acceder a variables globales
_lock = threading.Lock()

_question_event = threading.Event()
_web_response = None

def update_dashboard_state(update_dict: dict):
    with _lock:
        for k, v in update_dict.items():
            if k in _state:
                if k == "recent_tool_calls":
                    _state[k].insert(0, v)
                    _state[k] = _state[k][:10]  # Limitar a las últimas 10
                else:
                    _state[k] = v

def add_dashboard_log(log_line: str):
    with _lock:
        _logs.append(log_line)
        if len(_logs) > 50:
            _logs.pop(0)

def add_security_alert(alert_line: str):
    with _lock:
        _security_alerts.append(alert_line)
        if len(_security_alerts) > 20:
            _security_alerts.pop(0)

def set_pending_question(question: str):
    global _web_response
    with _lock:
        _state["pending_question"] = question
        _web_response = None
        _question_event.clear()

def clear_pending_question():
    with _lock:
        _state["pending_question"] = None

def submit_web_response(response: str):
    global _web_response
    with _lock:
        _web_response = response
        _question_event.set()

def get_web_response():
    return _web_response

def wait_for_response(timeout=None):
    return _question_event.wait(timeout)


class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Desactivar logs por consola de peticiones HTTP para mantener limpia la consola
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/respond":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                response_text = data.get("response", "")
                submit_web_response(response_text)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

    def do_GET(self):
        if self.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with _lock:
                response_data = {
                    "state": _state,
                    "logs": _logs,
                    "security_alerts": _security_alerts
                }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
            html = r"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PsychoSv_503 AI DevOS - Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #080c14;
            --card-bg: #111827;
            --text-color: #f3f4f6;
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.4);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border-color: #1f2937;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            padding: 24px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }

        h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-badge {
            padding: 8px 16px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 0 10px var(--primary-glow);
        }

        .status-idle { background-color: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid #6366f1; }
        .status-running { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; animation: pulse 2s infinite; }
        .status-failed { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
        .status-completed { background-color: rgba(16, 185, 129, 0.25); color: #10b981; border: 1px solid #10b981; }

        @keyframes pulse {
            0% { opacity: 0.6; box-shadow: 0 0 5px rgba(16, 185, 129, 0.2); }
            50% { opacity: 1; box-shadow: 0 0 20px rgba(16, 185, 129, 0.6); }
            100% { opacity: 0.6; box-shadow: 0 0 5px rgba(16, 185, 129, 0.2); }
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-4px);
            border-color: var(--primary);
            box-shadow: 0 12px 20px -3px rgba(99, 102, 241, 0.15);
        }

        .card h2 {
            font-size: 1.25rem;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            color: #9ca3af;
            font-weight: 600;
        }

        .metric {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--text-color);
            background: linear-gradient(to right, #34d399, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric-sub {
            font-size: 0.85rem;
            color: #9ca3af;
            margin-top: 6px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            font-size: 0.95rem;
        }

        .info-label { color: #9ca3af; }
        .info-value { font-weight: 600; color: #f3f4f6; }

        .terminal-card {
            grid-column: span 2;
        }

        .terminal {
            background-color: #030712;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            height: 350px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: #d1d5db;
            line-height: 1.6;
        }

        .alert-box {
            background-color: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 10px;
            padding: 12px 18px;
            color: #f87171;
            margin-top: 12px;
            font-size: 0.9rem;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        th { color: #9ca3af; font-weight: 600; }

        .tool-success { color: var(--success); font-weight: bold; }
        .tool-fail { color: var(--danger); font-weight: bold; }

        /* Estilos de Barra de Progreso */
        .progress-bar-bg {
            background: #1f2937;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
            position: relative;
        }

        .progress-bar-fill {
            background: linear-gradient(90deg, #6366f1, #a855f7);
            height: 100%;
            width: 0%;
            transition: width 0.4s ease;
        }

        .steps-nodes {
            display: flex;
            justify-content: space-between;
            position: relative;
        }

        .step-node {
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 0.75rem;
            color: #6b7280;
            position: relative;
            z-index: 2;
        }

        .step-dot {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #1f2937;
            border: 2px solid #374151;
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }

        .step-node.completed .step-dot {
            background: var(--success);
            border-color: var(--success);
            box-shadow: 0 0 8px var(--success);
        }

        .step-node.active .step-dot {
            background: var(--primary);
            border-color: var(--primary);
            box-shadow: 0 0 10px var(--primary);
            animation: pulse 1.5s infinite;
        }

        .step-node.completed {
            color: var(--success);
        }

        .step-node.active {
            color: var(--primary);
            font-weight: 600;
        }

        /* Interactive Panel style */
        .interactive-card {
            border: 2px solid #a855f7;
            background: linear-gradient(135deg, #151c2c, #1e1b4b);
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from { transform: translateY(-10px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .input-response {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #4b5563;
            background: #0b0f19;
            color: white;
            font-family: inherit;
            font-size: 0.95rem;
            margin-bottom: 12px;
        }

        .btn-submit {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            background: #a855f7;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .btn-submit:hover {
            background: #be185d;
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>PsychoSv_503 AI DevOS - Command Center</h1>
            <p style="color: #9ca3af; font-size: 0.95rem; margin-top: 6px;">Consola Militar de Orquestación y Control de Agentes Autónomos</p>
        </div>
        <div id="status-container" class="status-badge status-idle">IDLE</div>
    </header>

    <!-- Panel de Interacción Humana (Ask User) -->
    <div id="question-card" class="card interactive-card" style="display: none; margin-bottom: 24px;">
        <h2 style="color: #a855f7; border-bottom-color: rgba(168, 85, 247, 0.3);">💬 INTERVENCIÓN REQUERIDA (Human-in-the-Loop)</h2>
        <p id="question-text" style="margin-bottom: 16px; font-size: 1.1rem; font-weight: 500; line-height: 1.5;"></p>
        <div>
            <textarea id="response-input" class="input-response" placeholder="Escribe tu respuesta para el agente aquí..." rows="3"></textarea>
            <button onclick="submitResponse()" class="btn-submit">Enviar Respuesta</button>
        </div>
    </div>

    <!-- Progreso del Workflow -->
    <div class="card" id="workflow-progress-card" style="display: none; margin-bottom: 24px;">
        <h2>Progreso del Workflow</h2>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" id="progress-fill"></div>
        </div>
        <div class="steps-nodes" id="steps-nodes">
            <!-- Nodos insertados dinámicamente -->
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Agente Activo</h2>
            <div class="info-row"><span class="info-label">ID:</span><span class="info-value" id="val-agent">Ninguno</span></div>
            <div class="info-row"><span class="info-label">Rol:</span><span class="info-value" id="val-role">Ninguno</span></div>
            <div class="info-row"><span class="info-label">Proyecto:</span><span class="info-value" id="val-project">Ninguno</span></div>
            <div class="info-row"><span class="info-label">Workflow:</span><span class="info-value" id="val-workflow">Ninguno</span></div>
        </div>

        <div class="card">
            <h2>Métricas de Costo y Uso</h2>
            <div class="metric" id="val-cost">$0.0000</div>
            <div class="metric-sub">Costo de Tokens Estimado (USD)</div>
            <div style="margin-top: 15px;">
                <div class="info-row"><span class="info-label">Tokens Entrada:</span><span class="info-value" id="val-tokens-in">0</span></div>
                <div class="info-row"><span class="info-label">Tokens Salida:</span><span class="info-value" id="val-tokens-out">0</span></div>
                <div class="info-row"><span class="info-label">Llamadas Totales:</span><span class="info-value" id="val-calls">0</span></div>
            </div>
        </div>

        <div class="card terminal-card">
            <h2>Consola Web Formateada</h2>
            <div class="terminal" id="terminal-output">Esperando ejecución de workflows...</div>
        </div>
    </div>

    <div class="grid">
        <div class="card" style="grid-column: span 2;">
            <h2>Últimas Herramientas Ejecutadas (MCP)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Herramienta</th>
                        <th>Argumentos</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody id="tool-table-body">
                    <tr>
                        <td colspan="3" style="text-align: center; color: #9ca3af;">Ninguna herramienta ejecutada aún</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Incidentes de Seguridad</h2>
            <div id="security-alerts-container">
                <p style="color: #9ca3af; font-size: 0.9rem;">No se han detectado incidentes de seguridad.</p>
            </div>
        </div>
    </div>

    <script>
        function formatLogLine(line) {
            let escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            // Colores por patrones y niveles
            if (escaped.includes("ERROR") || escaped.includes("Fallo")) {
                return `<span style="color: #ef4444; font-weight: bold;">${escaped}</span>`;
            }
            if (escaped.includes("WARNING") || escaped.includes("QualityGate: Fallo") || escaped.includes("fallido")) {
                return `<span style="color: #fbbf24;">${escaped}</span>`;
            }
            if (escaped.includes("SUCCESS") || escaped.includes("finalizado con estado") || escaped.includes("COMPLETED")) {
                return `<span style="color: #34d399; font-weight: 500;">${escaped}</span>`;
            }
            if (escaped.includes("[SHUTDOWN]") || escaped.includes("cerrado ordenadamente")) {
                return `<span style="color: #c084fc; font-weight: bold;">${escaped}</span>`;
            }
            if (escaped.includes("QualityGate")) {
                return `<span style="color: #60a5fa; font-weight: bold;">${escaped}</span>`;
            }
            
            // Resaltar tags de agentes e.g. [psycho-ceo]
            escaped = escaped.replace(/(\[[a-zA-Z0-9_-]+\])/g, '<span style="color: #818cf8; font-weight: 600;">$1</span>');
            return escaped;
        }

        function submitResponse() {
            const val = document.getElementById('response-input').value;
            if (!val.trim()) return;
            fetch('/api/respond', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ response: val })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('question-card').style.display = 'none';
                document.getElementById('response-input').value = '';
            })
            .catch(err => alert("Error enviando respuesta: " + err));
        }

        function updateDashboard() {
            fetch('/api/state')
                .then(res => res.json())
                .then(data => {
                    // Actualizar estado general
                    const badge = document.getElementById('status-container');
                    badge.textContent = data.state.status;
                    badge.className = 'status-badge ' + 
                        (data.state.status === 'RUNNING' ? 'status-running' : 
                         data.state.status === 'FAILED' ? 'status-failed' : 
                         data.state.status === 'COMPLETED' ? 'status-completed' : 'status-idle');

                    document.getElementById('val-agent').textContent = data.state.active_agent;
                    document.getElementById('val-role').textContent = data.state.active_role;
                    document.getElementById('val-project').textContent = data.state.project_name;
                    document.getElementById('val-workflow').textContent = data.state.workflow_id;

                    // Actualizar tokens y costos
                    document.getElementById('val-cost').textContent = '$' + data.state.estimated_cost_usd.toFixed(4);
                    document.getElementById('val-tokens-in').textContent = data.state.input_tokens.toLocaleString();
                    document.getElementById('val-tokens-out').textContent = data.state.output_tokens.toLocaleString();
                    document.getElementById('val-calls').textContent = data.state.total_calls;

                    // Pregunta pendiente
                    const qCard = document.getElementById('question-card');
                    if (data.state.pending_question) {
                        document.getElementById('question-text').textContent = data.state.pending_question;
                        qCard.style.display = 'block';
                    } else {
                        qCard.style.display = 'none';
                    }

                    // Progress bar
                    const progressCard = document.getElementById('workflow-progress-card');
                    if (data.state.all_steps && data.state.all_steps.length > 0) {
                        progressCard.style.display = 'block';
                        const total = data.state.all_steps.length;
                        const completedCount = data.state.completed_steps ? data.state.completed_steps.length : 0;
                        const percentage = total > 0 ? (completedCount / total) * 100 : 0;
                        document.getElementById('progress-fill').style.width = percentage + '%';

                        // Actualizar nodos
                        const nodesContainer = document.getElementById('steps-nodes');
                        nodesContainer.innerHTML = '';
                        data.state.all_steps.forEach((step, idx) => {
                            const node = document.createElement('div');
                            node.className = 'step-node';
                            
                            const isCompleted = data.state.completed_steps && data.state.completed_steps.includes(step);
                            const isActive = data.state.active_agent === step;

                            if (isCompleted) node.classList.add('completed');
                            if (isActive) node.classList.add('active');

                            node.innerHTML = `
                                <div class="step-dot"></div>
                                <span>${step}</span>
                            `;
                            nodesContainer.appendChild(node);
                        });
                    } else {
                        progressCard.style.display = 'none';
                    }

                    // Actualizar logs terminal
                    const term = document.getElementById('terminal-output');
                    if (data.logs.length > 0) {
                        const formattedLogs = data.logs.map(formatLogLine);
                        term.innerHTML = formattedLogs.join('\\n');
                        term.scrollTop = term.scrollHeight;
                    } else {
                        term.textContent = 'Esperando ejecución de workflows...';
                    }

                    // Actualizar tabla de herramientas
                    const tableBody = document.getElementById('tool-table-body');
                    if (data.state.recent_tool_calls.length > 0) {
                        tableBody.innerHTML = '';
                        data.state.recent_tool_calls.forEach(call => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td><strong>\${call.tool}</strong></td>
                                <td><code>\${JSON.stringify(call.args)}</code></td>
                                <td class="\${call.status === 'SUCCESS' ? 'tool-success' : 'tool-fail'}">\${call.status}</td>
                            `;
                            tableBody.appendChild(tr);
                        });
                    }

                    // Actualizar alertas de seguridad
                    const secContainer = document.getElementById('security-alerts-container');
                    if (data.security_alerts.length > 0) {
                        secContainer.innerHTML = '';
                        data.security_alerts.forEach(alert => {
                            const div = document.createElement('div');
                            div.className = 'alert-box';
                            div.textContent = alert;
                            secContainer.appendChild(div);
                        });
                    } else {
                        secContainer.innerHTML = '<p style="color: #9ca3af; font-size: 0.9rem;">No se han detectado incidentes de seguridad.</p>';
                    }
                })
                .catch(err => console.error("Error actualizando dashboard:", err));
        }

        setInterval(updateDashboard, 1000);
        updateDashboard();
    </script>
</body>
</html>
"""
            self.wfile.write(html.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def start_dashboard_server():
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        pass

    try:
        server = ThreadingHTTPServer(("localhost", PORT), DashboardHTTPRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        logger.info(f"Servidor del Dashboard de Observabilidad iniciado en http://localhost:{PORT}")
        return server
    except Exception as e:
        logger.warning(f"El servidor del Dashboard ya se encuentra corriendo o falló el binding al puerto {PORT}: {str(e)}")
        return None
