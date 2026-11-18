"""Formatos de entrada y salida de la API (validación con Pydantic)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Prioridad = Literal["baja", "media", "alta"]


class TareaCrear(BaseModel):
    titulo: str = Field(min_length=1, max_length=120, examples=["Comprar dominio"])
    descripcion: str | None = Field(default=None, max_length=2000)
    prioridad: Prioridad = "media"


class TareaActualizar(BaseModel):
    """Todos los campos son opcionales: solo se cambia lo que se envía."""

    titulo: str | None = Field(default=None, min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=2000)
    prioridad: Prioridad | None = None
    completada: bool | None = None


class TareaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descripcion: str | None
    prioridad: Prioridad
    completada: bool
    creada: datetime
    actualizada: datetime


class ListaTareas(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    tareas: list[TareaSalida]


class Resumen(BaseModel):
    total: int
    completadas: int
    pendientes: int
    por_prioridad: dict[str, int]
