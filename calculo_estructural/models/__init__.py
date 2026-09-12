"""Modelos de datos (Pydantic) del dominio de conexiones estructurales.

Este paquete define únicamente la forma y las reglas intrínsecas de cada
entidad de datos. NO contiene:

- validaciones cruzadas entre entidades (ver ``calculo_estructural.validation``)
- fórmulas de cálculo o de resistencia (ver ``calculo_estructural.calculos``)
"""

from __future__ import annotations

from .base import MM_POR_PULGADA, ProyectoBaseModel, PuntoCoordenado, requerir_si
from .cargas import Cargas
from .configuracion_proyecto import ConfiguracionProyecto
from .elemento_concreto import ElementoConcreto
from .enums import (
    TipoAcero,
    TipoCombinacionCarga,
    TipoElementoConcreto,
    TipoGradoPerno,
    TipoSeccionPerfil,
    TipoSoldadura,
)
from .perfil_metalico import (
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilMetalico,
    PerfilRectangular,
)
from .pernos import Pernos, PosicionPerno
from .placa_base import Perforacion, PlacaBase
from .proyecto import MetadatosProyecto, Proyecto, VERSION_FORMATO_ACTUAL
from .soldadura import Soldadura

__all__ = [
    "MM_POR_PULGADA",
    "ProyectoBaseModel",
    "PuntoCoordenado",
    "requerir_si",
    "TipoAcero",
    "TipoCombinacionCarga",
    "TipoElementoConcreto",
    "TipoGradoPerno",
    "TipoSeccionPerfil",
    "TipoSoldadura",
    "ConfiguracionProyecto",
    "PlacaBase",
    "Perforacion",
    "PerfilMetalico",
    "PerfilRectangular",
    "PerfilCuadrado",
    "PerfilCircular",
    "PerfilI",
    "PerfilH",
    "ElementoConcreto",
    "Pernos",
    "PosicionPerno",
    "Soldadura",
    "Cargas",
    "MetadatosProyecto",
    "Proyecto",
    "VERSION_FORMATO_ACTUAL",
]
