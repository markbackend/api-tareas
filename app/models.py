"""Tablas de la base de datos."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def ahora() -> datetime:
    return datetime.now(timezone.utc)


class Tarea(Base):
    __tablename__ = "tareas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(120), index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, default=None)
    prioridad: Mapped[str] = mapped_column(String(10), default="media")
    completada: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    creada: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
    actualizada: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, onupdate=ahora)
