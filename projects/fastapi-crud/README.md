# FastAPI CRUD - DevOS v1 Demo

Este es un proyecto mínimo ejecutable generado por el **Personal AI DevOS v1** para demostrar capacidades de ingeniería Full-Stack.

## Características
- **FastAPI**: Framework web de alto rendimiento.
- **PostgreSQL**: Base de datos relacional.
- **SQLAlchemy**: ORM para gestión de modelos.
- **Docker**: Containerización completa.
- **Quality Gate**: Validado por el motor de calidad del DevOS.

## Cómo ejecutar
1. Asegúrate de tener Docker y Docker Compose instalados.
2. Ejecuta: `docker-compose up --build`
3. Accede a la documentación interactiva en: `http://localhost:8000/docs`

## Estructura
```
app/
  models/      # Definición de tablas SQLAlchemy
  schemas/     # Modelos Pydantic para validación
  routes/      # Endpoints de la API
  services/    # Lógica de negocio (CRUD)
  database.py  # Configuración de conexión
  main.py      # Punto de entrada
```
