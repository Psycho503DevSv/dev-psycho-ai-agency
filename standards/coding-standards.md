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

## 4. ESTILO VISUAL Y UI (Diseño Exótico, Moderno y Premium)
- **Estética Inmersiva Fuera de lo Común:** Las interfaces deben destacar de inmediato, evitando los diseños planos convencionales. Uso libre y creativo de estilos no tradicionales, animaciones dinámicas y componentes de alto impacto visual.
- **Gradientes y Colores de Alto Impacto:** Uso de gradientes de texto exóticos y desvanecimientos multitono (2 o 3 colores en armonía como acentos principales) para títulos y elementos de llamada a la acción.
- **Tipografía Exótica y Fluida:** Fuentes no tradicionales y combinaciones tipográficas modernas seleccionadas por el agente. Todo debe escalar automáticamente con fórmulas fluidas (`clamp()`, `vw`, `vh`).
- **Fondos Vivos de Libre Criterio:** Integrar fondos dinámicos basados en Canvas/WebGL que aporten vida al diseño. Pueden simular redes neuronales, dinámicas de fluidos, auroras cambiantes, ondas de plasma o partículas de luz, a criterio del agente para que el producto final se vea espectacular e impresionante.
- **Estructuras de Materiales Modernos:** Uso de Glassmorphism elegante (`backdrop-filter: blur`), sombras tridimensionales suaves y bordes ultra finos con iluminación sutil.
- **Microinteracciones Dinámicas:** Efectos interactivos fluidos y animaciones (desplazamientos 3D de tarjetas, botones holográficos, y transiciones elásticas) al pasar el cursor o hacer clic.

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
