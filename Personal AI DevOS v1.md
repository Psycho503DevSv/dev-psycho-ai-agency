Personal AI DevOS v1

Objetivo

Crear un ecosistema de agentes, estándares, MCPs y flujos de trabajo capaz de desarrollar:

- Web Apps
- APK Android
- Aplicaciones Desktop (.exe)
- APIs
- SaaS
- Herramientas internas

Compatible con:

- OpenCode
- Antigravity
- Claude
- Gemini CLI
- GPT
- Grok
- Qwen
- Modelos futuros

---

FASE 0 - PRINCIPIOS

Regla #1

Ningún agente escribe código inmediatamente.

Siempre:

1. Analizar requisitos.
2. Revisar documentación.
3. Validar arquitectura.
4. Detectar riesgos.
5. Planificar.
6. Implementar.

---

Regla #2

Toda decisión importante debe quedar documentada.

---

Regla #3

Todo cambio genera documentación.

---

Regla #4

Toda funcionalidad debe poder mantenerse después.

---

FASE 1 - NÚCLEO DEL SISTEMA

Crear:

/standards
/agents
/workflows
/templates
/docs
/mcps

---

FASE 2 - ESTÁNDARES

coding-standards.md

Define:

- Arquitectura
- Nombres
- Patrones
- Testing
- Modularidad

---

ui-standards.md

Tu estilo personal:

- Inspiración Linear
- Inspiración Vercel
- Inspiración Apple
- Dark Mode primero
- Responsive siempre
- Interfaces limpias
- Sin Bootstrap genérico
- Componentes reutilizables

---

animation-standards.md

Reglas:

- Animaciones suaves
- No animaciones excesivas
- Microinteracciones
- Feedback visual
- Motion premium

Aplicable a:

- Web
- APK
- Desktop

---

security-standards.md

Reglas:

- Sanitización
- Validación
- Rate limits
- RBAC
- Secrets seguros
- OWASP

---

database-standards.md

Reglas:

- SQL documentado
- Migraciones obligatorias
- Índices
- Relaciones
- Auditoría

---

FASE 3 - AGENTES PRINCIPALES

1. Discovery Agent

Responsabilidad:

Antes de iniciar cualquier proyecto preguntar:

- Objetivo
- Usuarios
- Alcance
- Tecnologías
- Restricciones
- Monetización
- Seguridad

No permite iniciar sin requisitos claros.

---

2. Solution Architect

Responsabilidad:

Diseñar:

- Arquitectura
- Estructura
- Stack
- Integraciones

Genera:

architecture.md

---

3. UI/UX Designer

Responsabilidad:

Diseño visual.

Aplica:

ui-standards.md

Nunca toca backend.

---

4. Animation Designer

Responsabilidad:

Diseñar movimiento.

Genera:

motion-specs.md

Aplica a:

- Web
- Android
- Desktop

---

5. Frontend Engineer

Implementación visual.

---

6. Backend Engineer

Implementación lógica.

---

7. Database Architect

Responsabilidad:

- PostgreSQL
- Supabase
- MySQL

Genera:

- schema.sql
- migrations
- documentación

---

8. Security Engineer

Responsabilidad:

Analizar:

- Vulnerabilidades
- Secretos
- Exposición

Debe revisar antes de producción.

---

9. Documentation Engineer

Responsabilidad:

Actualizar:

- README
- CHANGELOG
- Arquitectura
- API

Después de cada cambio.

---

10. QA Engineer

Responsabilidad:

Pruebas.

---

11. Code Reviewer

Responsabilidad:

- Detectar duplicados
- Detectar deuda técnica
- Detectar errores

---

12. Git Manager

Responsabilidad:

- Commits
- Branches
- Changelog

---

FASE 4 - MCPs

Mínimos:

Filesystem
Git
GitHub
Terminal
Chrome DevTools

---

Intermedios:

Docker
PostgreSQL
Supabase
OpenAPI
Figma

---

Avanzados:

Android Emulator
Playwright
Sentry
Cloudflare
AWS

---

FASE 5 - FLUJO OBLIGATORIO

Discovery Agent

↓

Solution Architect

↓

UI Designer

↓

Animation Designer

↓

Frontend/Backend

↓

Database Architect

↓

Security Review

↓

QA

↓

Documentation

↓

Git Manager

---

Nadie puede saltarse el flujo.

---

FASE 6 - DOCUMENTACIÓN AUTOMÁTICA

Todo cambio actualiza:

README.md

CHANGELOG.md

ARCHITECTURE.md

API.md

SECURITY.md

DATABASE.md

---

FASE 7 - SEGURIDAD

Cada release debe revisar:

- SQL Injection
- XSS
- CSRF
- Secrets
- Auth
- Permisos

---

FASE 8 - ESCALABILIDAD

Añadir futuros agentes:

DevOps Engineer

Cloud Architect

AI Engineer

Mobile Specialist

Desktop Specialist

Reverse Engineer

Performance Engineer

Cost Optimization Engineer

---

META FINAL

Construir una empresa virtual de agentes reutilizable en cualquier modelo de IA durante los próximos años.