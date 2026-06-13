# MEMORY STRATEGY: JERARQUÍA Y CICLO DE VIDA
## AI DevOS Orchestrator Module

### 1. CAPAS DE MEMORIA (DATA TIERS)

| Capa | Nombre | Ubicación | Regla de Retención |
| :--- | :--- | :--- | :--- |
| **L1** | **Hot Memory** | RAM / Runtime | Borrada al finalizar el turno. Solo datos inmediatos. |
| **L2** | **Working Memory** | `memories/session/` | Persiste durante la sesión activa. Resumen de estados. |
| **L3** | **Project Memory** | `memories/repo/` | Específica del repositorio actual. Decadencia baja. |
| **L4** | **Knowledge Memory**| `memories/global/` | Patrones de diseño y preferencias del usuario. |
| **L5** | **Long-Term** | `memory/sessions/` | Logs históricos y auditorías para entrenamiento futuro. |

### 2. REGLAS DE PROMOCIÓN (UPGRADE)
- **L1 $\rightarrow$ L2:** Si un dato es referenciado más de 3 veces en un turno, debe persistir en la sesión.
- **L2 $\rightarrow$ L3:** Al cerrar un hito (milestone), el resumen de la solución se mueve a la memoria del repositorio.
- **L3 $\rightarrow$ L4:** Si un patrón de error se repite en 3 proyectos distintos, se suma a las "Lecciones Globales".

### 3. REGLAS DE DEGRADACIÓN (DOWNGRADE/PRUNING)
- **Obsolescencia:** Si una versión de librería cambia (ej. React 17 $\rightarrow$ 18), los datos de L3 sobre la versión antigua se marcan como `DEPRECATED`.
- **Ruido:** Logs de terminal de hace > 5 turnos se eliminan de L2 para ahorrar tokens.
- **Conflicto:** Si una memoria de L4 contradice la Constitución actual, la memoria se borra.

### 4. MEMORY RETRIEVAL (Operational RAG)
El Orchestrator no busca texto plano, busca **Semántica Operacional**:
1. Intentar `get-context-from-metadata`.
2. Si falla, ejecutar `semantic-search` con top_k=5.
3. Validar frescura del dato (Timestamp < 24h).

### 5. CASO DE ERROR
- **Error:** Memory Mismatch (La memoria dice que el archivo existe, pero el FS dice que no).
- **Recuperación:** Invalidar L2/L3 para ese path, ejecutar `git status` y re-indexar.

### 6. EJEMPLO DE NOTA TÉCNICA (L3)
```yaml
id: MEM-2024-001
topic: "Uso de Redis en Windows"
lesson: "Requiere WSL2 o Docker; no hay soporte nativo estable."
status: active
timestamp: 2024-05-20T10:00:00Z
```
