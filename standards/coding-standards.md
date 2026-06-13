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

## 4. ESTILO VISUAL Y UI (Estilo Terminal Militar Prohibida 2085)
- **Estética Inmersiva Obligatoria:** Las interfaces no deben parecer dashboards corporativos planos tradicionales (como Trello/Jira). Deben recordar a una terminal militar clasificada del año 2085 con estética Cyberpunk, Blade Runner, e interfaces tácticas tipo JARVIS/Ghost in the Shell.
- **Sistemas de Materiales y Colores Exóticos:** Uso preferencial de Graphene Black, Titanium Silver, Electric Cyan y Aurora Violet/Blue. Estructuras con Glassmorphic con bordes HUD de color neón y esquinas tácticas tipo corchetes.
- **Fondos Vivos Interactivos:** Utilizar siempre un motor de fondo vivo animado interactivo (con Canvas/WebGL) que simule redes neuronales, partículas de plasma, niebla volumétrica y escáneres láser.
- **Tipografía Fluid & clamp():** Toda fuente y espaciado debe escalar automáticamente usando fórmulas fluidas (`clamp()`, `vw`, `vh`) para garantizar que la interfaz mantenga simetría matemática desde una mini pantalla de 2 pulgadas hasta una pantalla gigante o TV de 100 pulgadas sin romperse.
- **Microinteracciones Exageradas y 3D:** Tarjetas con efectos interactivos de inclinación 3D (Z-axis perspective shift), botones con brillo holográfico al pasar el mouse, animaciones elásticas y efectos de texto cifrado/descifrado (text-scramble) al renderizar contenido.
- **Iconografía Activa:** Los iconos deben tener comportamiento operacional (pulsos, órbitas, rotaciones o efectos de radar).

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
