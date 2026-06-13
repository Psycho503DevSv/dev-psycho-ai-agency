# AGENT SCORING ENGINE: FIABILIDAD Y REPUTACIÓN
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Mantener un registro dinámico del rendimiento de cada agente especialista para optimizar el ruteo futuro y la calidad del sistema.

### 2. MÉTRICAS DE REPUTACIÓN ($Rep$)
El score de cada agente se calcula tras cada tarea:
- **Accuracy (Precisión):** % de tareas que pasan los Quality Gates al primer intento. (40%).
- **Resilience (Resiliencia):** Capacidad de recuperarse de errores de terminal sin ayuda. (20%).
- **Compliance (Cumplimiento):** Apego estricto a la Constitución y protocolos de handover. (30%).
- **Efficienty (Eficiencia):** Consumo de tokens vs output generado. (10%).

### 3. ESCALA DE FIABILIDAD
- **0.9 - 1.0 (PRO):** El agente puede operar en modo autónomo total dentro de su dominio.
- **0.7 - 0.8 (STABLE):** Requiere revisión aleatoria de resultados.
- **0.5 - 0.6 (TRAINEE):** Requiere supervisión constante de cada paso.
- **< 0.5 (CRITICAL):** El agente es retirado del registry para "re-tuning" o actualización de sus instrucciones.

### 4. RECOMPENSAS Y PENALIZACIONES
- **Promoción:** Un agente con record perfecto puede ser "ascendido" a roles con más permisos MCP.
- **Penalización:** Alucinaciones detectadas por el Orchestrator bajan el score en 0.2 puntos inmediatamente.

### 5. PERSISTENCIA
Los scores se guardan en `registry/agent-registry.json` y persisten entre proyectos para que el Orchestrator "conozca" a su equipo con el tiempo.

### 6. EJEMPLO DE FICHA DE AGENTE
```json
{
  "agent_id": "ai-engineer-01",
  "score": 0.92,
  "top_skill": "Typescript Refactoring",
  "weakness": "Docker Config",
  "last_audit": "2024-06-13"
}
```
