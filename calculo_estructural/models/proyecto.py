"""Modelo raíz del proyecto: agrega metadatos y todas las secciones de
datos de entrada de la conexión."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .base import ProyectoBaseModel
from .cargas import Cargas
from .elemento_concreto import ElementoConcreto
from .perfil_metalico import PerfilMetalico
from .pernos import Pernos
from .placa_base import PlacaBase
from .soldadura import Soldadura

VERSION_FORMATO_ACTUAL = "1.0"
"""Versión del formato de archivo de proyecto (para migraciones futuras)."""


class MetadatosProyecto(ProyectoBaseModel):
    """Información descriptiva del proyecto (no interviene en los cálculos)."""

    nombre: str = Field(min_length=1, description="Nombre del proyecto")
    descripcion: str = ""
    autor: str = ""
    fecha_creacion: datetime
    fecha_modificacion: datetime


class Proyecto(ProyectoBaseModel):
    """Proyecto completo: metadatos + las seis secciones de datos de
    entrada de la conexión.

    Cada sección es opcional (``None``) hasta que el usuario la completa
    desde su formulario correspondiente; una vez completada, todos sus
    campos internos son obligatorios (lo garantiza el propio sub-modelo).
    """

    version_formato: str = VERSION_FORMATO_ACTUAL
    metadatos: MetadatosProyecto

    placa_base: PlacaBase | None = None
    perfil_metalico: PerfilMetalico | None = None
    elemento_concreto: ElementoConcreto | None = None
    pernos: Pernos | None = None
    soldadura: Soldadura | None = None
    cargas: Cargas | None = None
