# Guía de Configuración y Setup — [Nombre del Proyecto]

## 1. Prerequisitos
- Python 3.10+
- Node.js 18+
- Docker Desktop

## 2. Variables de Entorno
Copia `.env.example` a `.env` y llena los valores requeridos:
```bash
cp .env.example .env
```

| Variable | Descripción | Requerida |
|---|---|---|
| `EXAMPLE_KEY` | Descripción de la variable | ✅ |

## 3. Instalación de Dependencias
> Los agentes ejecutarán estos comandos vía MCP terminal. Solo debes aprobarlos.

```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## 4. Ejecución Local
```bash
# Backend
uvicorn app.main:app --reload

# Frontend
npm run dev
```

---
*Actualizado por: [Agente DevOps] | Fecha: [YYYY-MM-DD]*
