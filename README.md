# API de Tareas

API REST para gestionar tareas, hecha con **FastAPI**, **SQLAlchemy 2** y **SQLite**.
Incluye validación de datos, filtros, búsqueda, paginación, resumen estadístico y pruebas automáticas.

## Tecnologías

- Python 3.12
- FastAPI + Pydantic v2 (validación y documentación automática)
- SQLAlchemy 2 (ORM) con SQLite; cambia a PostgreSQL o MySQL con la variable `DATABASE_URL`
- Pytest (7 pruebas, base de datos en memoria por prueba)

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | Comprueba que la API está funcionando |
| POST | `/tareas` | Crea una tarea |
| GET | `/tareas` | Lista tareas. Filtros: `completada`, `prioridad`, `buscar`. Paginación: `pagina`, `por_pagina` |
| GET | `/tareas/resumen` | Totales: completadas, pendientes y por prioridad |
| GET | `/tareas/{id}` | Devuelve una tarea |
| PATCH | `/tareas/{id}` | Actualiza solo los campos enviados |
| DELETE | `/tareas/{id}` | Borra una tarea |

Las prioridades válidas son `baja`, `media` y `alta`. Los datos inválidos devuelven `422` y las tareas
inexistentes `404`.

## Cómo usarla

```bash
python -m venv .venv
.venv\Scripts\activate        # en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abrí **http://127.0.0.1:8000/docs** para probar todos los endpoints desde el navegador (Swagger UI).

### Ejemplo

```bash
curl -X POST http://127.0.0.1:8000/tareas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Comprar dominio", "prioridad": "alta"}'
```

```json
{
  "id": 1,
  "titulo": "Comprar dominio",
  "descripcion": null,
  "prioridad": "alta",
  "completada": false,
  "creada": "2026-11-18T10:00:00Z",
  "actualizada": "2026-11-18T10:00:00Z"
}
```

## Pruebas

```bash
pytest -q
```

## Estructura

```
app/
  main.py       # endpoints
  models.py     # tablas (SQLAlchemy)
  schemas.py    # validación de entrada y salida (Pydantic)
  database.py   # conexión y sesiones
tests/
  test_tareas.py
```
