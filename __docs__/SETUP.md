# Guía de Instalación y Configuración (SETUP)

Esta guía detalla los pasos para instalar, configurar y ejecutar PsychoSv_503 AI DevOS.

## 1. Requisitos Previos

* Python 3.10 o superior instalado en el sistema.
* Acceso a internet para llamadas a API de LLM (NVIDIA NIM o OpenAI).
* Clave de API de NVIDIA NIM (puedes obtener una gratis en [NVIDIA Build](https://build.nvidia.com/)).

## 2. Instalación de Dependencias

Puedes usar el entorno virtual pre-configurado `.venv` o el entorno global de tu máquina.

Instalar dependencias necesarias:
```bash
pip install -r requirements.txt
```

Las dependencias principales son:
* `requests`: Para llamadas HTTP directas a las APIs de inferencia.
* `python-dotenv`: Para la carga automática de variables de entorno desde el archivo `.env`.
* `openai`: Soporte opcional para llamadas OpenAI de compatibilidad.
* `graphiti-core`: Soporte opcional para base de datos de grafos de memoria semántica.

## 3. Configuración del Archivo `.env`

Crea o edita el archivo `.env` en la raíz del proyecto. Debe incluir lo siguiente:

```env
# Clave del API gratuita de NVIDIA NIM (Recomendada)
NVIDIA_API_KEY=tu_clave_aquí

# Clave de OpenAI (Opcional, si deseas usar GPT-4o-mini en su lugar)
OPENAI_API_KEY=

# Configuración de base de datos de grafos (Opcional, desactivada por defecto)
USE_GRAPHITI=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 4. Ejecución del Conjunto de Pruebas (Test Suite)

Para comprobar que tu entorno esté funcionando al 100%, ejecuta las pruebas unitarias usando `pytest`:

```bash
pytest
```

Verás que pasará el 100% de las 15 pruebas unitarias del framework.

## 5. Ejecución de Workflows

Puedes arrancar un workflow de agentes con el siguiente comando:

```bash
python -m runtime.workflow_runner <id-de-workflow> <nombre-del-proyecto>
```

Ejemplo para iniciar un proyecto de descubrimiento:
```bash
python -m runtime.workflow_runner wf-discovery mi-proyecto-demo
```

Esto ejecutará los pasos definidos en `workflows/wf-discovery.json` y creará la salida estructurada en la carpeta `projects/mi-proyecto-demo/`.

---
*Actualizado por: DevOps Agent | Fecha: 2026-06-15*
