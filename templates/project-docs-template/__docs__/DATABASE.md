# Base de Datos — SQL Scripts & Migraciones — [Nombre del Proyecto]

> Este archivo es el registro oficial de todos los scripts SQL del proyecto.
> Cada modificación al schema debe quedar aquí documentada y lista para ejecutarse.
> El agente Backend ejecuta estas migraciones vía MCP terminal. Este archivo sirve como auditoría humana.

---

## Schema Inicial — v1.0.0 — [YYYY-MM-DD]

### Descripción
> Creación inicial de las tablas del sistema.

```sql
-- =============================================
-- Tabla: users
-- Descripción: Almacena los usuarios del sistema
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    is_admin    BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Índice para búsquedas rápidas por email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

---

## Migración — v1.1.0 — [YYYY-MM-DD]

### Descripción
> Añade columna `full_name` a la tabla `users`.

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
```

---

## Datos Semilla (Seeds) — v1.0.0 — [YYYY-MM-DD]

### Descripción
> Inserta el usuario administrador por defecto.

```sql
INSERT INTO users (email, password, is_admin)
VALUES ('admin@devos.ai', 'hashed_password_aqui', TRUE)
ON CONFLICT (email) DO NOTHING;
```

---

## Guía de Ejecución

Los agentes ejecutan estas migraciones automáticamente vía MCP terminal.
Para ejecutarlas manualmente si fuera necesario:

```bash
# PostgreSQL
psql -U postgres -d nombre_bd -f __docs__/database_init.sql

# SQLite (desarrollo)
sqlite3 ./dev.db < __docs__/database_init.sql
```

---
*Actualizado por: [Agente Backend] | Fecha: [YYYY-MM-DD]*
