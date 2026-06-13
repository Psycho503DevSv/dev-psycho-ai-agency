# ESTÁNDARES DE CODIFICACIÓN (CODING STANDARDS)

## 1. FILOSOFÍA DE DESARROLLO
Desarrollamos código que sea fácil de leer, mantener y escalar. La elegancia nunca debe sacrificar la claridad.

## 2. ARQUITECTURA PREFERIDA
- **Modularidad:** Separación clara de responsabilidades (SoC). Un archivo debe hacer una sola cosa bien.
- **Clean Architecture:** Independencia de frameworks, UI y bases de datos.
- **DRY (Don't Repeat Yourself):** Abstraer lógica común en utilidades o componentes reutilizables en `/templates`.

## 3. CONVENCIONES DE NOMBRADO (SINTAXIS TÉCNICA)
A pesar de la política de idioma, los identificadores de código siguen el estándar de la industria (Inglés):
- **Clases:** `PascalCase` (ej. `UserManager`).
- **Funciones/Variables:** `camelCase` (ej. `getUserById`).
- **Constantes:** `UPPER_SNAKE_CASE` (ej. `MAX_RETRY_ATTEMPTS`).
- **Tablas BD:** `snake_case_plural` (ej. `user_profiles`).

## 4. ESTILO VISUAL Y UI (Basado en Linear/Vercel)
- **Modo Oscuro Primero:** El diseño base siempre debe considerar el Dark Mode.
- **Minimalismo:** Eliminar elementos que no aporten a la tarea del usuario.
- **Feedback Visual:** Implementar microinteracciones y estados de carga en cada acción del sistema.
- **Responsive:** Mobile-first es el estándar para Web Apps.

## 5. TESTING Y CALIDAD
- **TDD (Test Driven Development) Recomendado:** Escribir el test antes que la funcionalidad.
- **Cobertura Mínima:** 80% en lógica de negocio crítica.
- **Pruebas E2E:** Obligatorias para flujos críticos (Login, Checkout, etc.) usando Playwright.

## 6. COMENTARIOS Y DOCUMENTACIÓN DE CÓDIGO
- **JSDoc/Docstrings:** Todas las funciones públicas deben estar documentadas con parámetros y tipos de retorno.
- **El "Por qué", no el "Qué":** El código describe el "qué", los comentarios deben explicar el "por qué" de las decisiones complejas.
- **Idioma de Comentarios:** Las explicaciones dentro del código deben ser en **español**, siguiendo la política global.

## 7. EJEMPLO PRÁCTICO
```typescript
/**
 * Obtiene el perfil de usuario validando permisos de seguridad.
 * Aplica el Estándar de Seguridad Nivel 2.
 */
async function fetchUserProfile(userId: string): Promise<User> {
    // Validar sanitize
    const cleanId = sanitizeInput(userId);
    return await db.query('SELECT * FROM users WHERE id = $1', [cleanId]);
}
```

---
*Jerarquía de Decisión: Nivel 3. Alineado con Arquitectura y Constitución.*
