import http.server
import socketserver
import json
import os
import threading
import logging

PORT = 8050
logger = logging.getLogger("Dashboard")

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
    "recent_tool_calls": []
}

_logs = []
_security_alerts = []

# Bloqueo para evitar colisiones de hilos al acceder a variables globales
_lock = threading.Lock()

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

class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Desactivar logs por consola de peticiones HTTP para mantener limpia la consola
        pass

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
            
            html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PsychoSv_503 AI DevOS - Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --text-color: #f3f4f6;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border-color: #2e3b52;
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
            padding: 20px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(to right, #6366f1, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
        }

        .status-idle { background-color: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid #6366f1; }
        .status-running { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; animation: pulse 2s infinite; }
        .status-failed { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
        }

        .card h2 {
            font-size: 1.1rem;
            margin-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            color: #9ca3af;
        }

        .metric {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-color);
        }

        .metric-sub {
            font-size: 0.85rem;
            color: #9ca3af;
            margin-top: 5px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 0.95rem;
        }

        .info-label { color: #9ca3af; }
        .info-value { font-weight: 600; }

        .terminal-card {
            grid-column: span 2;
        }

        .terminal {
            background-color: #05070c;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: #10b981;
        }

        .alert-box {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 10px 15px;
            color: #f87171;
            margin-top: 10px;
            font-size: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid var(--border-color);
        }

        th { color: #9ca3af; }

        .tool-success { color: var(--success); }
        .tool-fail { color: var(--danger); }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>PsychoSv_503 AI DevOS</h1>
            <p style="color: #9ca3af; font-size: 0.9rem; margin-top: 4px;">Panel de Control y Observabilidad de Agentes en Vivo</p>
        </div>
        <div id="status-container" class="status-badge status-idle">IDLE</div>
    </header>

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
            <h2>Monitoreo en Tiempo Real (Workflows)</h2>
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
        function updateDashboard() {
            fetch('/api/state')
                .then(res => res.json())
                .then(data => {
                    // Actualizar estado general
                    const badge = document.getElementById('status-container');
                    badge.textContent = data.state.status;
                    badge.className = 'status-badge ' + 
                        (data.state.status === 'RUNNING' ? 'status-running' : 
                         data.state.status === 'FAILED' ? 'status-failed' : 'status-idle');

                    document.getElementById('val-agent').textContent = data.state.active_agent;
                    document.getElementById('val-role').textContent = data.state.active_role;
                    document.getElementById('val-project').textContent = data.state.project_name;
                    document.getElementById('val-workflow').textContent = data.state.workflow_id;

                    // Actualizar tokens y costos
                    document.getElementById('val-cost').textContent = '$' + data.state.estimated_cost_usd.toFixed(4);
                    document.getElementById('val-tokens-in').textContent = data.state.input_tokens.toLocaleString();
                    document.getElementById('val-tokens-out').textContent = data.state.output_tokens.toLocaleString();
                    document.getElementById('val-calls').textContent = data.state.total_calls;

                    // Actualizar logs terminal
                    const term = document.getElementById('terminal-output');
                    if (data.logs.length > 0) {
                        term.textContent = data.logs.join('\\n');
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

    server = ThreadingHTTPServer(("localhost", PORT), DashboardHTTPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    logger.info(f"Servidor del Dashboard de Observabilidad iniciado en http://localhost:{PORT}")
    return server
