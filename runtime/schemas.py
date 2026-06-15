# schemas.py — runtime/
# Esquemas Pydantic V2 para validación estricta de interfaces y payloads

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

# ─── MCP EXECUTOR SCHEMAS ──────────────────────────────────────────────────

class CommandSchema(BaseModel):
    command: str = Field(..., description="Comando terminal de shell a ser ejecutado en el sandbox o localmente.")

    @field_validator("command")
    @classmethod
    def command_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El comando no puede estar vacío.")
        return v.strip()

class ExecutionResultSchema(BaseModel):
    status: str = Field(..., description="Resultado de la ejecución, típicamente 'SUCCESS' o 'FAILED'.")
    stdout: str = Field("", description="Salida estándar del comando.")
    stderr: str = Field("", description="Salida de error del comando.")
    code: int = Field(-1, description="Código de salida del proceso.")
    sandbox: str = Field("local", description="Entorno donde se ejecutó: 'local' o 'docker'.")
    message: Optional[str] = Field(None, description="Mensaje explicativo o de error descriptivo.")

# ─── AUTO LEARNER SCHEMAS ──────────────────────────────────────────────────

class LessonSchema(BaseModel):
    id: str = Field(..., description="Identificador único legible de la lección aprendida.")
    phase: str = Field(..., description="Fase o componente donde se aplica (ej. 'backend', 'executor', 'mcp').")
    trigger: str = Field(..., description="Condición o patrón de error que activa esta lección.")
    action: str = Field(..., description="Instrucción de corrección o mitigación a seguir.")
    confidence: float = Field(0.9, description="Nivel de confianza o validez de la lección (0.0 a 1.0).")

class LearningPayloadSchema(BaseModel):
    lessons: List[LessonSchema] = Field(default_factory=list, description="Lista de lecciones extraídas para aprendizaje.")

# ─── QUALITY GATE SCHEMAS ──────────────────────────────────────────────────

class GateDecisionSchema(BaseModel):
    approved: bool = Field(..., description="True si pasa todos los controles de calidad, False en caso contrario.")
    score: float = Field(..., description="Puntuación de calidad asignada (escala 0.0 a 10.0).")
    reasons: List[str] = Field(default_factory=list, description="Lista de explicaciones para la aprobación o rechazo.")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones detalladas para mejorar el código.")
