"""Validaciones cruzadas entre entidades y del proyecto completo.

A diferencia de ``calculo_estructural.models`` (reglas propias de cada
entidad, ya garantizadas al construir el objeto), este paquete solo
contiene reglas que necesitan más de una entidad del proyecto para
evaluarse. Ninguna regla de este paquete calcula resistencia ni aplica
una fórmula normativa: son compatibilidad geométrica y de datos.

Módulos por categoría: ``pernos_perforaciones``, ``geometria_placa``,
``pernos_concreto``, ``soldadura_perfil`` y ``cargas``. ``proyecto``
orquesta todos sobre un ``Proyecto`` completo.
"""

from __future__ import annotations

from . import configuracion
from .proyecto import hay_errores, resumen_por_estado, validar_proyecto
from .resultados import Componente, EstadoValidacion, ResultadoValidacion

__all__ = [
    "configuracion",
    "hay_errores",
    "resumen_por_estado",
    "validar_proyecto",
    "Componente",
    "EstadoValidacion",
    "ResultadoValidacion",
]
