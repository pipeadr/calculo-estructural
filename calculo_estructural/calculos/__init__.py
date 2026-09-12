"""Cálculos geométricos básicos (sin fórmulas de resistencia).

Usados por las validaciones cruzadas (``calculo_estructural.validation``)
y por el módulo de dibujo (``calculo_estructural.dibujo``): dimensiones
envolventes, contorno y perímetro de un perfil, y distancia entre puntos.
"""

from __future__ import annotations

from .propiedades_geometricas import (
    bounding_box_perfil,
    contorno_perfil_ih,
    distancia_entre_puntos,
    perimetro_perfil,
)

__all__ = [
    "bounding_box_perfil",
    "contorno_perfil_ih",
    "distancia_entre_puntos",
    "perimetro_perfil",
]
