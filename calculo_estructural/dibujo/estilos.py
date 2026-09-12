"""Colores y primitivas de dibujo compartidas entre las vistas.

No contiene geometría de ningún componente específico (eso vive en
``vista_planta.py`` / ``seccion_transversal.py``): solo utilidades
genéricas de Matplotlib que ambas vistas reutilizan.
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Arc, Circle

COLOR_PLACA = "#8a8a8a"
COLOR_PERFIL = "#2b6cb0"
COLOR_PERFORACION = "#ffffff"
COLOR_PERFORACION_BORDE = "#333333"
COLOR_PERNO = "#c05621"
COLOR_CONCRETO = "#b7a99a"
COLOR_EJE = "#999999"
COLOR_COTA = "#444444"
COLOR_CARGA = "#c53030"


def dibujar_cota(
    ax: Axes,
    p1: tuple[float, float],
    p2: tuple[float, float],
    texto: str,
    *,
    desplazamiento: float = 0.0,
    color: str = COLOR_COTA,
) -> None:
    """Línea de cota (con flechas en ambos extremos) entre dos puntos
    alineados horizontal o verticalmente, con su texto centrado.

    ``desplazamiento`` mueve la línea perpendicular al segmento p1-p2,
    para no encimarla con el contorno que está acotando.
    """
    x1, y1 = p1
    x2, y2 = p2
    vertical = abs(x2 - x1) < abs(y2 - y1)
    if vertical:
        x1 += desplazamiento
        x2 += desplazamiento
    else:
        y1 += desplazamiento
        y2 += desplazamiento

    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="<->", color=color, linewidth=0.8, shrinkA=0, shrinkB=0),
    )
    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(
        xm,
        ym,
        f" {texto} ",
        color=color,
        fontsize=8,
        ha="center",
        va="center",
        rotation=90 if vertical else 0,
        backgroundcolor="white",
    )


def dibujar_vector_fuera_de_plano(
    ax: Axes,
    centro: tuple[float, float],
    positivo: bool,
    etiqueta: str,
    *,
    radio: float = 15.0,
    color: str = COLOR_CARGA,
) -> None:
    """Notación estándar de un vector perpendicular al plano del dibujo:
    círculo con punto central (saliente, positivo) o con aspa (entrante,
    negativo). Es notación matemática de diagramas de cuerpo libre, no
    una interpretación de ingeniería (eso queda a criterio de
    ``Cargas.convencion_signos``)."""
    x, y = centro
    ax.add_patch(Circle((x, y), radio, fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    if positivo:
        ax.plot(x, y, marker="o", markersize=4, color=color, zorder=6)
    else:
        offset = radio * 0.6
        ax.plot([x - offset, x + offset], [y - offset, y + offset], color=color, linewidth=1.2, zorder=6)
        ax.plot([x - offset, x + offset], [y + offset, y - offset], color=color, linewidth=1.2, zorder=6)
    ax.text(x, y - radio - 4, etiqueta, color=color, fontsize=8, ha="center", va="top")


def dibujar_momento_curvo(
    ax: Axes,
    centro: tuple[float, float],
    positivo: bool,
    etiqueta: str,
    *,
    radio: float = 20.0,
    color: str = COLOR_CARGA,
) -> None:
    """Momento como flecha curva alrededor de ``centro``. Sentido
    antihorario = positivo (regla de la mano derecha con el eje
    correspondiente saliendo hacia el observador)."""
    x, y = centro
    theta1, theta2 = 20, 340
    ax.add_patch(Arc((x, y), 2 * radio, 2 * radio, angle=0, theta1=theta1, theta2=theta2, color=color, linewidth=1.4))

    punta_angulo, cola_angulo = (theta2, theta2 - 12) if positivo else (theta1, theta1 + 12)
    punta = (x + radio * np.cos(np.radians(punta_angulo)), y + radio * np.sin(np.radians(punta_angulo)))
    cola = (x + radio * np.cos(np.radians(cola_angulo)), y + radio * np.sin(np.radians(cola_angulo)))
    ax.annotate(
        "",
        xy=punta,
        xytext=cola,
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1.4, mutation_scale=10, shrinkA=0, shrinkB=0),
    )
    ax.text(x, y - radio - 4, etiqueta, color=color, fontsize=8, ha="center", va="top")


def dibujar_flecha(
    ax: Axes,
    origen: tuple[float, float],
    destino: tuple[float, float],
    etiqueta: str,
    *,
    color: str = COLOR_CARGA,
) -> None:
    """Flecha recta simple (fuerza en el plano del dibujo) con su
    etiqueta junto a la punta. El largo de la flecha es el que le pase
    el llamador (no es proporcional a la magnitud de la carga: esta vista
    no calcula ni representa distribución de esfuerzos)."""
    ax.annotate(
        "",
        xy=destino,
        xytext=origen,
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1.6, mutation_scale=14, shrinkA=0, shrinkB=0),
    )
    ax.text(destino[0], destino[1], f" {etiqueta}", color=color, fontsize=8, va="center")
