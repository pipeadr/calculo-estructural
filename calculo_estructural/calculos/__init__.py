"""Cálculos geométricos básicos (sin fórmulas de resistencia).

Esta etapa solo incluye lo estrictamente necesario para las validaciones
cruzadas de ``calculo_estructural.validation``: dimensiones envolventes y
perímetro de un perfil, y distancia entre puntos. El resto (centroide del
grupo de pernos, áreas, propiedades para dibujo) se agrega cuando la Fase
1 llegue a la etapa de dibujo.
"""

from __future__ import annotations

from .propiedades_geometricas import (
    bounding_box_perfil,
    distancia_entre_puntos,
    perimetro_perfil,
)

__all__ = ["bounding_box_perfil", "distancia_entre_puntos", "perimetro_perfil"]
