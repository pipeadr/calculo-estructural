"""Cálculos geométricos básicos de las secciones ya definidas en los
modelos de datos: dimensiones envolventes, perímetro exterior y distancia
entre puntos.

Importante: este módulo NO contiene fórmulas de resistencia ni de
comportamiento estructural (áreas de corte, inercias, capacidades, etc.)
— solo geometría pura, usada por las validaciones cruzadas (Etapa 2) y,
más adelante, por el módulo de dibujo.
"""

from __future__ import annotations

import numpy as np

from ..models import (
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilMetalico,
    PerfilRectangular,
)


def bounding_box_perfil(perfil: PerfilMetalico) -> tuple[float, float]:
    """Dimensiones ``(ancho_x_mm, ancho_y_mm)`` del rectángulo envolvente
    del perfil, centrado en su propio centroide.

    Se usa para verificar que el perfil cabe dentro de la placa; no tiene
    relación con propiedades de resistencia.
    """
    if isinstance(perfil, PerfilRectangular):
        return perfil.b_mm, perfil.h_mm
    if isinstance(perfil, PerfilCuadrado):
        return perfil.lado_mm, perfil.lado_mm
    if isinstance(perfil, PerfilCircular):
        return perfil.diametro_mm, perfil.diametro_mm
    if isinstance(perfil, (PerfilI, PerfilH)):
        return perfil.ancho_ala_mm, perfil.peralte_mm
    raise TypeError(f"Tipo de perfil no reconocido: {type(perfil)!r}")


def perimetro_perfil(perfil: PerfilMetalico) -> float:
    """Perímetro del contorno exterior de la sección, en mm (para
    perfiles tubulares, solo el contorno externo, sin el hueco interior).

    Se usa para comparar con la longitud de soldadura declarada; no es
    una propiedad de resistencia.
    """
    if isinstance(perfil, PerfilRectangular):
        return 2 * (perfil.b_mm + perfil.h_mm)
    if isinstance(perfil, PerfilCuadrado):
        return 4 * perfil.lado_mm
    if isinstance(perfil, PerfilCircular):
        return float(np.pi * perfil.diametro_mm)
    if isinstance(perfil, (PerfilI, PerfilH)):
        # Trazando el contorno de ala ancha (12 lados: 2 alas de ancho bf,
        # 2 caras de alma de altura d-2*tf, 4 cantos de ala de espesor tf
        # y 4 escalones ala-alma de (bf-tw)/2) se simplifica a:
        #   2*bf + 4*tf + 2*(d-2*tf) + 2*(bf-tw) = 4*bf + 2*d - 2*tw
        return 4 * perfil.ancho_ala_mm + 2 * perfil.peralte_mm - 2 * perfil.espesor_alma_mm
    raise TypeError(f"Tipo de perfil no reconocido: {type(perfil)!r}")


def distancia_entre_puntos(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Distancia euclidiana entre dos puntos (x, y), en la misma unidad
    en la que vengan expresados ambos puntos."""
    return float(np.hypot(p1[0] - p2[0], p1[1] - p2[1]))
