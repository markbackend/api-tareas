import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def cliente():
    """Cada prueba usa una base de datos nueva en memoria."""
    motor = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=motor)
    Sesion = sessionmaker(bind=motor, expire_on_commit=False)

    def db_de_prueba():
        db = Sesion()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_de_prueba
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def crear(cliente, **datos):
    respuesta = cliente.post("/tareas", json={"titulo": "Tarea", **datos})
    assert respuesta.status_code == 201
    return respuesta.json()


def test_salud(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}


def test_crear_y_obtener(cliente):
    tarea = crear(cliente, titulo="Comprar dominio", prioridad="alta")
    assert tarea["completada"] is False
    assert cliente.get(f"/tareas/{tarea['id']}").json()["titulo"] == "Comprar dominio"


def test_validacion(cliente):
    assert cliente.post("/tareas", json={"titulo": ""}).status_code == 422
    assert cliente.post("/tareas", json={"titulo": "x", "prioridad": "urgente"}).status_code == 422


def test_listar_filtrar_y_paginar(cliente):
    for i in range(5):
        crear(cliente, titulo=f"Tarea {i}", prioridad="alta" if i % 2 else "baja")
    datos = cliente.get("/tareas", params={"prioridad": "alta"}).json()
    assert datos["total"] == 2
    pagina2 = cliente.get("/tareas", params={"por_pagina": 2, "pagina": 2}).json()
    assert pagina2["total"] == 5 and len(pagina2["tareas"]) == 2
    assert cliente.get("/tareas", params={"buscar": "tarea 3"}).json()["total"] == 1


def test_actualizar_parcial(cliente):
    tarea = crear(cliente, descripcion="original")
    actualizada = cliente.patch(f"/tareas/{tarea['id']}", json={"completada": True}).json()
    assert actualizada["completada"] is True
    assert actualizada["descripcion"] == "original"


def test_resumen(cliente):
    a = crear(cliente, prioridad="alta")
    crear(cliente, prioridad="baja")
    cliente.patch(f"/tareas/{a['id']}", json={"completada": True})
    assert cliente.get("/tareas/resumen").json() == {
        "total": 2,
        "completadas": 1,
        "pendientes": 1,
        "por_prioridad": {"baja": 1, "media": 0, "alta": 1},
    }


def test_borrar_y_404(cliente):
    tarea = crear(cliente)
    assert cliente.delete(f"/tareas/{tarea['id']}").status_code == 204
    assert cliente.get(f"/tareas/{tarea['id']}").status_code == 404
    assert cliente.delete("/tareas/999").status_code == 404
