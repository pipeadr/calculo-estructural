"""Guardado y carga de proyectos en JSON.

``guardar_proyecto`` / ``cargar_proyecto`` son las funciones públicas que
se espera que use la interfaz gráfica (Etapa 6); todas las excepciones
que pueden levantar heredan de ``ProyectoIOError``.
"""

from __future__ import annotations

from .excepciones import (
    ArchivoNoEncontradoError,
    DatosInvalidosError,
    EscrituraError,
    JSONInvalidoError,
    LecturaError,
    ProyectoIOError,
    VersionNoSoportadaError,
)
from .proyecto_io import VERSIONES_SOPORTADAS, ProyectoValidado, cargar_proyecto, guardar_proyecto

__all__ = [
    "ProyectoIOError",
    "ArchivoNoEncontradoError",
    "LecturaError",
    "EscrituraError",
    "JSONInvalidoError",
    "VersionNoSoportadaError",
    "DatosInvalidosError",
    "ProyectoValidado",
    "VERSIONES_SOPORTADAS",
    "guardar_proyecto",
    "cargar_proyecto",
]
