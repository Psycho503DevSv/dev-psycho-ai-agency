# Documentación de API — [Nombre del Proyecto]

## Autenticación
> Describe el método de autenticación (JWT, API Key, OAuth, etc.)

## Endpoints

### `POST /auth/register`
**Descripción:** Crea una nueva cuenta de usuario.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword"
}
```

**Respuesta 201:**
```json
{
  "id": 1,
  "email": "user@example.com"
}
```

---
*Actualizado por: [Agente Backend] | Fecha: [YYYY-MM-DD]*
