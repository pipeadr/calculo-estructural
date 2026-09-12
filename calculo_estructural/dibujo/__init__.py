"""Generación de figuras Matplotlib (vista en planta y sección
transversal) a partir de un ``Proyecto``.

Este paquete solo dibuja geometría y cargas ya definidas en ``models/``
(con ayuda de ``calculos/`` para dimensiones envolventes y contornos) —
no calcula ni representa resistencia ni distribución de esfuerzos.
"""

from __future__ import annotations

from .seccion_transversal import dibujar_seccion_transversal
from .vista_planta import dibujar_vista_planta

__all__ = ["dibujar_vista_planta", "dibujar_seccion_transversal"]
