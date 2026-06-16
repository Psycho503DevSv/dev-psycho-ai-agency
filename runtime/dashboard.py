import http.server
import socketserver
import json
import os
import threading
from typing import Optional

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
    "pending_question": None,
    "document_preview": None
}

_logs = []
_security_alerts = []

# Bloqueo para evitar colisiones de hilos al acceder a variables globales
_lock = threading.Lock()

_question_event = threading.Event()
_web_response = None

import re

def redact_secrets(data):
    """Ofusca claves API, tokens y contraseñas de manera recursiva."""
    if isinstance(data, str):
        redacted = data
        redacted = re.sub(r"\b(AIzaSy[a-zA-Z0-9_-]{33})\b", r"AIzaSy...", redacted)
        redacted = re.sub(r"\b(gsk_[a-zA-Z0-9_-]{40,})\b", r"gsk_...", redacted)
        redacted = re.sub(r"\b([0-9]+:[a-zA-Z0-9_-]{35})\b", r"TelegramToken_...", redacted)
        redacted = re.sub(r"(key|token|password|secret|pass|api_key|authorization|bearer)\b\s*[:=]\s*['\"][^'\"]{4,}['\"]", r"\1: '********'", redacted, flags=re.IGNORECASE)
        redacted = re.sub(r"(Bearer\s+)[a-zA-Z0-9_-]{15,}", r"\1********", redacted, flags=re.IGNORECASE)
        return redacted
    elif isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if k.lower() in ("key", "token", "password", "secret", "pass", "api_key", "authorization", "bearer"):
                new_dict[k] = "********"
            else:
                new_dict[k] = redact_secrets(v)
        return new_dict
    elif isinstance(data, list):
        return [redact_secrets(item) for item in data]
    return data

def update_dashboard_state(update_dict: dict):
    update_dict = redact_secrets(update_dict)
    with _lock:
        for k, v in update_dict.items():
            if k in _state:
                if k == "recent_tool_calls":
                    _state[k].insert(0, v)
                    _state[k] = _state[k][:10]  # Limitar a las últimas 10
                else:
                    _state[k] = v

def add_dashboard_log(log_line: str):
    log_line = redact_secrets(log_line)
    with _lock:
        _logs.append(log_line)
        if len(_logs) > 50:
            _logs.pop(0)

def add_security_alert(alert_line: str):
    with _lock:
        _security_alerts.append(alert_line)
        if len(_security_alerts) > 20:
            _security_alerts.pop(0)

def set_pending_question(question: str, document_preview: Optional[str] = None):
    global _web_response
    with _lock:
        _state["pending_question"] = question
        _state["document_preview"] = document_preview
        _web_response = None
        _question_event.clear()

def clear_pending_question():
    with _lock:
        _state["pending_question"] = None
        _state["document_preview"] = None

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
        if self.path == "/api/project":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                project_name = data.get("project", "")
                if project_name:
                    with _lock:
                        _state["project_name"] = project_name
                    # Crear directorio del proyecto en disco si no existe
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    project_dir = os.path.join(base_dir, "memory", "projects", project_name)
                    os.makedirs(project_dir, exist_ok=True)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok", "project": project_name}).encode("utf-8"))
                else:
                    raise ValueError("El nombre del proyecto es requerido.")
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

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
        if self.path in ("/data/fondo.webp", "/fondo.webp"):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "fondo.webp")
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/webp")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        if self.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with _lock:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                memory_projects_dir = os.path.join(base_dir, "memory", "projects")
                code_projects_dir = os.path.join(base_dir, "projects")
                
                available_set = set()
                if os.path.exists(memory_projects_dir):
                    available_set.update([d for d in os.listdir(memory_projects_dir) if os.path.isdir(os.path.join(memory_projects_dir, d))])
                if os.path.exists(code_projects_dir):
                    available_set.update([d for d in os.listdir(code_projects_dir) if os.path.isdir(os.path.join(code_projects_dir, d))])
                
                available_projects = sorted(list(available_set))
                
                response_data = {
                    "state": _state,
                    "logs": _logs,
                    "security_alerts": _security_alerts,
                    "available_projects": available_projects
                }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        if self.path.startswith("/api/requirements"):
            # Obtener el nombre del proyecto desde query string o usar el activo
            project_name = _state["project_name"]
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            if "project" in params:
                project_name = params["project"][0]

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            req_path = os.path.join(base_dir, "memory", "projects", project_name, "requirements.md")
            
            content = ""
            exists = False
            if project_name and project_name != "Ninguno" and os.path.exists(req_path):
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    exists = True
                except Exception as e:
                    content = f"Error leyendo requisitos: {str(e)}"
            else:
                content = f"No se han generado requerimientos todavía para el proyecto '{project_name}'."

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"exists": exists, "content": content, "project": project_name}).encode("utf-8"))
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
    <title>PsychoSv_503 AI DevOS - Cyberpunk Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: transparent;
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-color: #f3f4f6;
            --primary: #9d00ff;
            --cyan: #00f0ff;
            --magenta: #ff007f;
            --toxic-green: #39ff14;
            --blood-red: #ff0033;
            --border-color: rgba(0, 240, 255, 0.35);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: #030305;
            background-image: url('/data/fondo.webp');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            padding: 24px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--magenta);
            text-shadow: 0 0 10px rgba(255, 0, 127, 0.3);
            background: rgba(12, 6, 24, 0.22);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 24px;
        }

        h1 {
            font-family: 'Permanent Marker', cursive;
            font-size: 2.5rem;
            letter-spacing: 2px;
            color: var(--cyan);
            text-shadow: 2px 2px 0px var(--magenta), -2px -2px 0px #000;
        }

        .status-badge {
            font-family: 'Orbitron', sans-serif;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: 900;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            transform: skewX(-10deg);
            box-shadow: 0 0 15px var(--border-color);
        }

        .status-idle { background-color: rgba(157, 0, 255, 0.2); color: var(--primary); border: 2px solid var(--primary); box-shadow: 0 0 15px rgba(157, 0, 255, 0.4); }
        .status-running { background-color: rgba(0, 240, 255, 0.2); color: var(--cyan); border: 2px solid var(--cyan); box-shadow: 0 0 20px rgba(0, 240, 255, 0.6); animation: pulse 2s infinite; }
        .status-failed { background-color: rgba(255, 0, 51, 0.2); color: var(--blood-red); border: 2px solid var(--blood-red); box-shadow: 0 0 20px rgba(255, 0, 51, 0.6); }
        .status-completed { background-color: rgba(57, 255, 20, 0.2); color: var(--toxic-green); border: 2px solid var(--toxic-green); box-shadow: 0 0 20px rgba(57, 255, 20, 0.6); }

        @keyframes pulse {
            0% { opacity: 0.7; box-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }
            50% { opacity: 1; box-shadow: 0 0 25px rgba(0, 240, 255, 0.7); }
            100% { opacity: 0.7; box-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }

        .card {
            background: rgba(12, 6, 24, 0.22);
            backdrop-filter: blur(8px) saturate(160%);
            -webkit-backdrop-filter: blur(8px) saturate(160%);
            border: 1px solid rgba(0, 240, 255, 0.35);
            border-radius: 16px;
            padding: 24px;
            box-shadow:
                0 0 0 0.5px rgba(255,255,255,0.05) inset,
                0 8px 32px rgba(0, 0, 0, 0.2),
                0 0 15px rgba(0, 240, 255, 0.06);
            position: relative;
            overflow: hidden;
            transition: all 0.35s ease;
        }

        /* Cyberpunk corner decorations */
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 12px;
            height: 12px;
            border-top: 3px solid var(--magenta);
            border-left: 3px solid var(--magenta);
        }
        .card::after {
            content: '';
            position: absolute;
            bottom: 0;
            right: 0;
            width: 12px;
            height: 12px;
            border-bottom: 3px solid var(--cyan);
            border-right: 3px solid var(--cyan);
        }

        .card:hover {
            transform: scale(1.01) translateY(-3px);
            border-color: var(--cyan);
            background: rgba(22, 10, 45, 0.75);
            box-shadow:
                0 0 25px rgba(0, 240, 255, 0.4),
                0 0 60px rgba(157, 0, 255, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .card h2 {
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            font-size: 1.25rem;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--magenta);
            padding-bottom: 10px;
            color: var(--cyan) !important;
            text-shadow: 0 0 5px rgba(0, 240, 255, 0.3);
        }

        .metric {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 2.6rem;
            color: var(--toxic-green);
            background: linear-gradient(to right, var(--toxic-green), var(--cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(57, 255, 20, 0.3);
        }

        .metric-sub {
            font-size: 0.85rem;
            color: #9ca3af;
            margin-top: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            font-size: 0.95rem;
        }

        .info-label { color: #9ca3af; font-family: 'Orbitron', sans-serif; font-size: 0.85rem; }
        .info-value { font-weight: 600; color: var(--cyan); font-family: 'Share Tech Mono', monospace; font-size: 1.05rem; }

        .terminal-card, .span-2 {
            grid-column: span 2;
        }

        @media (max-width: 900px) {
            header {
                flex-direction: column;
                gap: 16px;
                text-align: center;
                align-items: center;
            }
            .terminal-card, .span-2 {
                grid-column: span 1 !important;
            }
            body {
                padding: 12px;
            }
            h1 {
                font-size: clamp(1.8rem, 5vw, 2.5rem);
            }
            .metric {
                font-size: 2.2rem;
            }
            .terminal {
                height: 280px;
                font-size: 0.85rem;
                padding: 12px;
            }
        }

        .terminal {
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 0, 127, 0.5);
            border-radius: 12px;
            padding: 20px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.9rem;
            height: 350px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: #ffffff;
            text-shadow: 0 0 4px rgba(0, 240, 255, 0.4);
            line-height: 1.7;
            box-shadow: inset 0 0 30px rgba(157, 0, 255, 0.06);
        }

        .alert-box {
            background-color: rgba(255, 0, 51, 0.1);
            border: 1.5px solid var(--blood-red);
            border-radius: 4px;
            padding: 12px 18px;
            color: #ff3355;
            margin-top: 12px;
            font-size: 0.9rem;
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-family: 'Share Tech Mono', monospace;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(255, 0, 51, 0.4);
            box-shadow: 0 0 15px rgba(255, 0, 51, 0.2);
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

        th { color: var(--magenta); font-family: 'Orbitron', sans-serif; font-weight: 700; text-transform: uppercase; }
        td { font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; }

        .tool-success { color: var(--toxic-green); font-weight: bold; }
        .tool-fail { color: var(--blood-red); font-weight: bold; }

        /* Progress track style */
        .progress-bar-bg {
            background: rgba(157, 0, 255, 0.15);
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 20px;
            position: relative;
            border: 1px solid var(--primary);
        }

        .progress-bar-fill {
            background: linear-gradient(90deg, var(--primary), var(--magenta), var(--cyan));
            height: 100%;
            width: 0%;
            transition: width 0.4s ease;
            box-shadow: 0 0 10px var(--cyan);
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
            font-size: 0.8rem;
            color: #6b7280;
            position: relative;
            z-index: 2;
        }

        .step-dot {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #0d0d1a;
            border: 2px solid var(--primary);
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }

        .step-node.completed .step-dot {
            background: var(--toxic-green);
            border-color: var(--toxic-green);
            box-shadow: 0 0 12px var(--toxic-green);
        }

        .step-node.active .step-dot {
            background: var(--cyan);
            border-color: var(--cyan);
            box-shadow: 0 0 15px var(--cyan);
            animation: pulse 1.5s infinite;
        }

        .step-node.completed {
            color: var(--toxic-green);
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
        }

        .step-node.active {
            color: var(--cyan);
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            text-shadow: 0 0 5px var(--cyan);
        }

        /* Interactive response card */
        .interactive-card {
            border: 2px solid var(--magenta);
            background: linear-gradient(135deg, rgba(21, 12, 36, 0.9), rgba(10, 5, 20, 0.95));
            box-shadow: 0 0 30px rgba(255, 0, 127, 0.35);
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from { transform: translateY(-10px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .input-response {
            width: 100%;
            padding: 12px;
            border-radius: 4px;
            border: 1px solid var(--magenta);
            background: #050508;
            color: white;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1rem;
            margin-bottom: 12px;
            box-shadow: inset 0 0 5px rgba(255, 0, 127, 0.2);
        }

        .input-response:focus {
            outline: none;
            border-color: var(--cyan);
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
        }

        .btn-submit {
            font-family: 'Orbitron', sans-serif;
            padding: 12px 24px;
            border-radius: 4px;
            border: none;
            background: linear-gradient(90deg, var(--magenta), var(--primary));
            color: white;
            font-weight: 900;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
            box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
        }

        .btn-submit:hover {
            background: linear-gradient(90deg, var(--cyan), var(--magenta));
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.6);
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>PsychoSv_503 AI DevOS</h1>
            <p style="color: #9ca3af; font-size: 0.95rem; margin-top: 6px; font-family: 'Orbitron', sans-serif; letter-spacing: 1px;">CENTRO DE ORQUESTACIÓN DE AGENTES DE ÉLITE</p>
        </div>
        <div id="status-container" class="status-badge status-idle">IDLE</div>
    </header>

    <!-- Panel de Interacción Humana (Ask User) -->
    <div id="question-card" class="card interactive-card" style="display: none; margin-bottom: 24px;">
        <h2 style="color: var(--magenta) !important; border-bottom-color: rgba(255, 0, 127, 0.3);">💬 INTERVENCIÓN REQUERIDA (Human-in-the-Loop)</h2>
        <p id="question-text" style="margin-bottom: 16px; font-size: 1.1rem; font-weight: 500; line-height: 1.5; font-family: 'Share Tech Mono', monospace; color: #fff;"></p>
        
        <!-- Previsualización del Documento -->
        <div id="doc-preview-section" style="display: none; margin-bottom: 16px;">
            <p class="info-label" style="margin-bottom: 6px;">📄 Previsualización del Borrador Generado:</p>
            <div id="doc-preview-content" class="terminal" style="height: 200px; font-family: 'Inter', sans-serif; white-space: pre-wrap; font-size: 0.95rem; padding: 12px; border-color: var(--magenta); background: rgba(157, 0, 255, 0.05); overflow-y: auto;"></div>
        </div>

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

    <!-- Panel de Selección de Proyecto y Requisitos -->
    <div class="grid">
        <div class="card">
            <h2>📁 Gestión de Proyectos</h2>
            <div style="margin-bottom: 16px;">
                <label for="project-selector" class="info-label" style="display:block; margin-bottom:8px;">Proyecto Activo:</label>
                <select id="project-selector" class="input-response" style="margin-bottom: 12px; width: 100%; cursor: pointer;" onchange="changeActiveProject(this.value)">
                    <option value="Ninguno">Ninguno</option>
                </select>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="new-project-input" class="input-response" style="margin-bottom: 0;" placeholder="Nuevo proyecto..." />
                    <button onclick="createNewProject()" class="btn-submit" style="padding: 10px; font-size: 0.85rem;">Crear</button>
                </div>
            </div>
        </div>

        <div class="card terminal-card" style="grid-column: span 1 !important; display: flex; flex-direction: column;">
            <h2>📝 Visor de Requisitos (requirements.md)</h2>
            <div id="requirements-viewer" class="terminal" style="flex-grow: 1; height: 200px; font-family: 'Inter', sans-serif; white-space: pre-wrap; font-size: 0.9rem; padding: 15px; border-color: var(--cyan); background: rgba(0, 5, 15, 0.4);">
                Selecciona un proyecto para cargar sus requisitos.
            </div>
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

        <div class="card terminal-card" style="position: relative; grid-column: span 1 !important;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2>Consola Web Formateada</h2>
                <button onclick="copyLogsToClipboard()" class="btn-submit" style="padding: 6px 12px; font-size: 0.8rem; margin: 0; box-shadow: 0 0 10px rgba(0, 240, 255, 0.4); background: linear-gradient(90deg, var(--cyan), var(--primary));">Copiar Logs</button>
            </div>
            <div class="terminal" id="terminal-output" style="height: 250px;">Esperando ejecución de workflows...</div>
        </div>
    </div>

    <div class="grid">
        <div class="card span-2" style="grid-column: span 1 !important;">
            <h2>Últimas Herramientas Ejecutadas (MCP)</h2>
            <div style="overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch;">
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
                            <td colspan="3" style="text-align: center; color: #9ca3af; font-family: 'Share Tech Mono', monospace;">Ninguna herramienta ejecutada aún</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card" style="grid-column: span 1 !important;">
            <h2>Incidentes de Seguridad</h2>
            <div id="security-alerts-container">
                <p style="color: #9ca3af; font-size: 0.9rem; font-family: 'Share Tech Mono', monospace;">No se han detectado incidentes de seguridad.</p>
            </div>
        </div>
    </div>

    <script>
        let lastProject = "";

        function formatLogLine(line) {
            let escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            // Colores por patrones y niveles del estilo cyberpunk
            if (escaped.includes("ERROR") || escaped.includes("Fallo")) {
                return `<span style="color: var(--blood-red); font-weight: bold;">${escaped}</span>`;
            }
            if (escaped.includes("WARNING") || escaped.includes("QualityGate: Fallo") || escaped.includes("fallido")) {
                return `<span style="color: var(--magenta); font-weight: bold;">${escaped}</span>`;
            }
            if (escaped.includes("SUCCESS") || escaped.includes("finalizado con estado") || escaped.includes("COMPLETED")) {
                return `<span style="color: var(--toxic-green); font-weight: bold;">${escaped}</span>`;
            }
            if (escaped.includes("[SHUTDOWN]") || escaped.includes("cerrado ordenadamente")) {
                return `<span style="color: var(--primary); font-weight: bold;">${escaped}</span>`;
            }
            if (escaped.includes("QualityGate")) {
                return `<span style="color: var(--cyan); font-weight: bold;">${escaped}</span>`;
            }
            
            // Resaltar tags de agentes e.g. [psycho-ceo]
            escaped = escaped.replace(/(\[[a-zA-Z0-9_-]+\])/g, '<span style="color: var(--cyan); font-weight: bold;">$1</span>');
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

        function changeActiveProject(projName) {
            if (!projName || projName === lastProject) return;
            fetch('/api/project', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project: projName })
            })
            .then(res => res.json())
            .then(data => {
                lastProject = projName;
                updateRequirements(projName);
            })
            .catch(err => console.error("Error al cambiar proyecto:", err));
        }

        function createNewProject() {
            const val = document.getElementById('new-project-input').value.trim();
            if (!val) return;
            // Sanitizar nombre
            const cleanName = val.toLowerCase().replace(/[^a-z0-9_-]/g, '-');
            changeActiveProject(cleanName);
            document.getElementById('new-project-input').value = '';
        }

        function updateRequirements(projName) {
            const viewer = document.getElementById('requirements-viewer');
            if (!projName || projName === 'Ninguno') {
                viewer.textContent = 'Selecciona un proyecto para cargar sus requisitos.';
                return;
            }
            fetch(`/api/requirements?project=\${encodeURIComponent(projName)}`)
            .then(res => res.json())
            .then(data => {
                viewer.textContent = data.content;
            })
            .catch(err => {
                viewer.textContent = "Error al conectar con la API de Requisitos: " + err;
            });
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

                    // Actualizar selector de proyectos
                    const selector = document.getElementById('project-selector');
                    const currentSel = selector.value;
                    
                    // Reconstruir opciones si es necesario
                    let optionsHtml = '<option value="Ninguno">Ninguno</option>';
                    if (data.available_projects && data.available_projects.length > 0) {
                        data.available_projects.forEach(p => {
                            optionsHtml += `<option value="\${p}">\${p}</option>`;
                        });
                    }
                    
                    // Agregar el proyecto actual si no está en la lista disponible físicamente
                    if (data.state.project_name && data.state.project_name !== 'Ninguno' && (!data.available_projects || !data.available_projects.includes(data.state.project_name))) {
                        optionsHtml += `<option value="\${data.state.project_name}">\${data.state.project_name}</option>`;
                    }
                    
                    selector.innerHTML = optionsHtml;
                    
                    // Mantener seleccionado el proyecto activo actual
                    if (data.state.project_name) {
                        selector.value = data.state.project_name;
                        if (data.state.project_name !== lastProject) {
                            lastProject = data.state.project_name;
                            updateRequirements(lastProject);
                        }
                    } else {
                        selector.value = 'Ninguno';
                    }

                    // Actualizar tokens y costos
                    document.getElementById('val-cost').textContent = '$' + data.state.estimated_cost_usd.toFixed(4);
                    document.getElementById('val-tokens-in').textContent = data.state.input_tokens.toLocaleString();
                    document.getElementById('val-tokens-out').textContent = data.state.output_tokens.toLocaleString();
                    document.getElementById('val-calls').textContent = data.state.total_calls;

                    // Pregunta pendiente
                    const qCard = document.getElementById('question-card');
                    if (data.state.pending_question) {
                        document.getElementById('question-text').textContent = data.state.pending_question;
                        
                        const docSection = document.getElementById('doc-preview-section');
                        const docContent = document.getElementById('doc-preview-content');
                        if (data.state.document_preview) {
                            docContent.textContent = data.state.document_preview;
                            docSection.style.display = 'block';
                        } else {
                            docSection.style.display = 'none';
                        }
                        
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
                                <span>\${step}</span>
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
                        term.innerHTML = formattedLogs.join('<br>');
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
                        secContainer.innerHTML = '<p style="color: #9ca3af; font-size: 0.9rem; font-family: \'Share Tech Mono\', monospace;">No se han detectado incidentes de seguridad.</p>';
                    }

                    // Auto-actualizar visor de requisitos solo cuando cambia el proyecto activo
                    const serverProject = data.state.project_name || 'Ninguno';
                    if (serverProject !== lastProject) {
                        lastProject = serverProject;
                        updateRequirements(lastProject);
                    }
                })
                .catch(err => console.error("Error actualizando dashboard:", err));
        }

        function copyLogsToClipboard() {
            const term = document.getElementById('terminal-output');
            const text = term.innerText || term.textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert("Logs copiados al portapapeles con éxito.");
            }).catch(err => {
                console.error("Error al copiar logs: ", err);
                const textarea = document.createElement("textarea");
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand("copy");
                    alert("Logs copiados al portapapeles con éxito (fallback).");
                } catch (e) {
                    alert("No se pudo copiar de forma automática. Por favor selecciona y copia manualmente.");
                }
                document.body.removeChild(textarea);
            });
        }

        setInterval(updateDashboard, 1500);
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
