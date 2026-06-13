# PYTHON CODING STANDARDS v1.0

## 1. ESTRUCTURA DE PROYECTOS
- Archivo principal: `main.py` o `<nombre_proyecto>.py`.
- Dependencias: `requirements.txt` (obligatorio).
- Pruebas: Carpeta `tests/` con archivos `test_*.py`.
- Documentación: `README.md` con instrucciones de uso.

## 2. CONVENCIONES DE NOMBRES
- Variables y funciones: `snake_case`.
- Clases: `PascalCase`.
- Constantes: `UPPER_SNAKE_CASE`.
- Módulos/Paquetes: `snake_case`.

## 3. CALIDAD Y CÓDIGO
- **Type Hints:** Obligatorios para argumentos y retornos de funciones/métodos.
- **Docstrings:** Estilo Google o ReST para clases y funciones públicas.
- **Logging:** Usar módulo `logging`. Prohibido `print()` para logs persistentes.
- **Manejo de Errores:** Try-Except específicos. Evitar `except Exception:`.

## 4. TESTING
- Framework: `unittest` o `pytest`.
- Cobertura mínima: 80%.
- Todo proyecto debe incluir al menos una prueba de integración (Happy Path).

## 5. REQUISITOS DE CI/CD (Quality Gate)
1.  **Sintaxis:** El código debe ser ejecutable sin errores de parseo.
2.  **Linting:** Seguir PEP 8 (máximo 88-120 caracteres por línea).
3.  **Archivos requeridos:** No se aprueba el workflow si falta `README.md` o `requirements.txt`.
