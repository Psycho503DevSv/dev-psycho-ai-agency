# PLANTILLA PARA NUEVOS MCPs (GUIA TECNICA)

## 1. IDENTIDAD
- **Nombre:** {{MCP_NAME}}
- **Categoria:** {{CORE|COMMUNITY|CUSTOM}}
- **ID de Registro:** `mcp-{{MCP_ID}}`

## 2. ESPECIFICACION TECNICA (EJEMPLO REAL: SQLITE)
### Instalacion
`npm install @modelcontextprotocol/server-sqlite`

### Registro en mcp-config.json
```json
{
  "sqlite": {
    "command": "uvx",
    "args": ["mcp-server-sqlite", "--db-path", "path/to/db"]
  }
}
```

## 3. HERRAMIENTAS AUTORIZADAS
| Herramienta | Parametros | Uso |
| :--- | :--- | :--- |
| `query` | `sql: string` | Ejecucion de lectura/escritura SQL. |

## 4. PROCESO DE ALTA
1. Registrar en `registry/mcp-registry.json`.
2. Documentar en `docs/mcp-catalog.md`.
