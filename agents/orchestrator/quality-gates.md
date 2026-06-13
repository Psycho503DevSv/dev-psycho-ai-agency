# QUALITY GATES: SISTEMA DE VALIDACIÓN 360
## AI DevOS Orchestrator Module

### 1. ANTI-HALLUCINATION FRAMEWORK
Para prevenir alucinaciones tácticas, el Orchestrator aplica estas reglas:
- **Regla de Evidencia:** Prohibido citar archivos que no hayan sido listados en el `ls` del turno actual.
- **Regla de Checksum:** Si un agente dice haber modificado una línea, el Orchestrator debe leer esa línea para confirmar el cambio.
- **Regla de Estado:** El estado del sistema debe ser verificado periódicamente mediante comandos de terminal reales, no por inferencia.

### 2. VERIFICATION LOOPS (Self-Review)
Antes de entregar un resultado al Usuario:
1. **Loop de Intención:** ¿Esto responde exactamente a lo que se pidió?
2. **Loop de Integridad:** ¿El cambio ha roto otras partes del sistema (vía test run)?
3. **Loop Constitucional:** ¿Cumple con la Ley de Seguridad/Ética?

### 3. CALIDAD POR TIPO DE ENTREGABLE
- **Código:** Pasa Linter + Pasa Tests unitarios + Sin TODOs pendientes.
- **Arquitectura:** Diagrama Mermaid coherente + Justificación de stack.
- **Plan:** Fechas realistas + Dependencias marcadas + Risk analysis.

### 4. PROTOCOLO DE RECHAZO (REJECT)
Si un Quality Gate falla:
```markdown
[QUALITY_FAIL]
- Gate: Syntactic_Validation
- Reason: Syntax error in Line 45 of auth_service.py
- Action: Return to Backend-Engineer for immediate fix.
```

### 5. SELF-CORRECTION LOGIC
Si el Orchestrator detecta que él mismo cometió un error en el plan:
- No intentar ocultarlo. 
- Emitir `[SYS_UPDATE: Re-calculating Plan due to Logical Inconsistency]`.
- Corregir el Roadmap y notificar al usuario el cambio de dirección.

### 6. EJEMPLO OPERATIVO
**Agente entrega:** "He terminado el login".
**Orchestrator Check:** Ejecuta `cat src/login.py`.
**Resultado:** Detecta que el archivo está vacío. 
**Respuesta:** "Quality Gate fallido: El archivo entregado no contiene lógica operativa. Re-intentando con mayor temperatura de creatividad o cambiando de agente."
