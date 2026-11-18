"""API REST de tareas: crear, listar, filtrar, actualizar y borrar."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .schemas import ListaTareas, Prioridad, Resumen, TareaActualizar, TareaCrear, TareaSalida


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API de Tareas",
    version="1.0.0",
    description="API REST de ejemplo con FastAPI, SQLAlchemy y SQLite.",
    lifespan=lifespan,
)


def buscar_tarea(db: Session, tarea_id: int) -> models.Tarea:
    tarea = db.get(models.Tarea, tarea_id)
    if tarea is None:
        raise HTTPException(status_code=404, detail=f"No existe la tarea {tarea_id}")
    return tarea


@app.get("/salud", tags=["sistema"])
def salud():
    return {"estado": "ok"}


@app.post("/tareas", response_model=TareaSalida, status_code=status.HTTP_201_CREATED, tags=["tareas"])
def crear_tarea(datos: TareaCrear, db: Session = Depends(get_db)):
    tarea = models.Tarea(**datos.model_dump())
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


@app.get("/tareas", response_model=ListaTareas, tags=["tareas"])
def listar_tareas(
    completada: bool | None = None,
    prioridad: Prioridad | None = None,
    buscar: str | None = Query(default=None, max_length=120, description="Texto a buscar en el título"),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = select(models.Tarea)
    if completada is not None:
        consulta = consulta.where(models.Tarea.completada == completada)
    if prioridad is not None:
        consulta = consulta.where(models.Tarea.prioridad == prioridad)
    if buscar:
        consulta = consulta.where(models.Tarea.titulo.ilike(f"%{buscar}%"))

    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    tareas = db.scalars(
        consulta.order_by(models.Tarea.id).offset((pagina - 1) * por_pagina).limit(por_pagina)
    ).all()
    return ListaTareas(total=total, pagina=pagina, por_pagina=por_pagina, tareas=tareas)


@app.get("/tareas/resumen", response_model=Resumen, tags=["tareas"])
def resumen(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(models.Tarea.id)))
    completadas = db.scalar(select(func.count(models.Tarea.id)).where(models.Tarea.completada.is_(True)))
    filas = db.execute(
        select(models.Tarea.prioridad, func.count(models.Tarea.id)).group_by(models.Tarea.prioridad)
    ).all()
    por_prioridad = {"baja": 0, "media": 0, "alta": 0} | {p: n for p, n in filas}
    return Resumen(total=total, completadas=completadas, pendientes=total - completadas, por_prioridad=por_prioridad)


@app.get("/tareas/{tarea_id}", response_model=TareaSalida, tags=["tareas"])
def obtener_tarea(tarea_id: int, db: Session = Depends(get_db)):
    return buscar_tarea(db, tarea_id)


@app.patch("/tareas/{tarea_id}", response_model=TareaSalida, tags=["tareas"])
def actualizar_tarea(tarea_id: int, datos: TareaActualizar, db: Session = Depends(get_db)):
    tarea = buscar_tarea(db, tarea_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(tarea, campo, valor)
    db.commit()
    db.refresh(tarea)
    return tarea


@app.delete("/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tareas"])
def borrar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    db.delete(buscar_tarea(db, tarea_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
