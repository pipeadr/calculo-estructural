"""Sección transversal de la conexión: corte a lo largo del eje X,
mostrando el perfil, la placa base, los pernos embebidos y el elemento de
concreto.

Es un corte esquemático: la longitud del perfil sobre la placa se dibuja
con una altura fija y nominal (``ALTURA_STUB_PERFIL_MM``), marcada con
una línea de corte en zigzag (convención de dibujo técnico para
elementos truncados) — la longitud real de la columna no es un dato de
este modelo. Todo elemento es opcional: si la sección correspondiente del
proyecto es ``None``, esa parte simplemente no se dibuja.
"""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from ..calculos import bounding_box_perfil
from ..models import ElementoConcreto, PerfilMetalico, Pernos, PlacaBase, Proyecto
from . import estilos

ALTURA_STUB_PERFIL_MM = 250.0
"""Altura fija y esquemática con la que se dibuja el perfil sobre la
placa (no es un dato del modelo: la longitud real de la columna no se
captura en esta fase)."""


def dibujar_seccion_transversal(proyecto: Proyecto) -> Figure:
    """Genera la ``Figure`` de la sección transversal para el estado
    actual del proyecto."""
    fig = Figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.set_title("Sección transversal (corte según X)")

    placa = proyecto.placa_base
    if placa is None:
        ax.text(0.5, 0.5, "Falta definir la placa base", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return fig

    y_tope_placa = 0.0
    y_base_placa = -placa.espesor_mm

    # El ancho visible tiene que cubrir el elemento más ancho de todos
    # (normalmente el concreto es más ancho que la placa) para que nada
    # quede recortado por los límites del eje.
    anchos_mm = [placa.largo_mm]
    if proyecto.elemento_concreto is not None:
        anchos_mm.append(proyecto.elemento_concreto.largo_mm)
    if proyecto.pernos is not None and proyecto.pernos.posiciones:
        anchos_mm.append(2 * max(abs(p.x_mm) for p in proyecto.pernos.posiciones))
    medio_ancho_total = max(anchos_mm) / 2
    carril = medio_ancho_total * 0.06 + 15.0  # separación entre líneas de cota consecutivas

    _dibujar_placa(ax, placa, y_tope_placa, y_base_placa, x_cota=medio_ancho_total + carril)
    if proyecto.elemento_concreto is not None:
        _dibujar_concreto(ax, proyecto.elemento_concreto, y_base_placa, x_cota=-(medio_ancho_total + carril))
    if proyecto.pernos is not None:
        _dibujar_pernos(ax, proyecto.pernos, y_base_placa, x_cota=medio_ancho_total + 2 * carril)
    if proyecto.perfil_metalico is not None:
        _dibujar_perfil(ax, proyecto.perfil_metalico, y_tope_placa)

    margen = medio_ancho_total * 0.35
    ax.set_xlim(-medio_ancho_total - margen, medio_ancho_total + margen)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Z (mm)")
    return fig


def _dibujar_placa(ax, placa: PlacaBase, y_tope: float, y_base: float, *, x_cota: float) -> None:
    medio_largo = placa.largo_mm / 2
    ax.add_patch(
        Rectangle(
            (-medio_largo, y_base),
            placa.largo_mm,
            placa.espesor_mm,
            facecolor=estilos.COLOR_PLACA,
            edgecolor="black",
            linewidth=1.2,
            zorder=3,
        )
    )
    estilos.dibujar_cota(ax, (x_cota, y_base), (x_cota, y_tope), f"e={placa.espesor_mm:g} mm")


def _dibujar_concreto(ax, concreto: ElementoConcreto, y_tope: float, *, x_cota: float) -> float:
    medio_largo = concreto.largo_mm / 2
    y_base = y_tope - concreto.altura_mm
    ax.add_patch(
        Rectangle(
            (-medio_largo, y_base),
            concreto.largo_mm,
            concreto.altura_mm,
            facecolor=estilos.COLOR_CONCRETO,
            edgecolor="black",
            linewidth=1.0,
            hatch="//",
            zorder=1,
        )
    )
    estilos.dibujar_cota(ax, (x_cota, y_base), (x_cota, y_tope), f"{concreto.altura_mm:g} mm")
    return y_base


def _dibujar_pernos(ax, pernos: Pernos, y_tope_embebido: float, *, x_cota: float) -> None:
    y_base = y_tope_embebido - pernos.profundidad_embebido_mm
    y_tope_libre = y_tope_embebido + max(pernos.longitud_mm - pernos.profundidad_embebido_mm, 0.0)

    xs_dibujadas: set[float] = set()
    for posicion in pernos.posiciones:
        x = round(posicion.x_mm, 6)
        if x in xs_dibujadas:
            # Varios pernos proyectan a la misma X (distinta Y): se
            # dibuja una sola varilla, como en un plano de elevación.
            continue
        xs_dibujadas.add(x)
        ax.plot([x, x], [y_base, y_tope_libre], color=estilos.COLOR_PERNO, linewidth=2.5, zorder=4)

    if pernos.posiciones:
        estilos.dibujar_cota(
            ax,
            (x_cota, y_tope_embebido),
            (x_cota, y_base),
            f"{pernos.profundidad_embebido_mm:g} mm",
        )


def _dibujar_perfil(ax, perfil: PerfilMetalico, y_base: float) -> None:
    ancho_x, _ = bounding_box_perfil(perfil)
    y_tope = y_base + ALTURA_STUB_PERFIL_MM
    ax.add_patch(
        Rectangle(
            (-ancho_x / 2, y_base),
            ancho_x,
            ALTURA_STUB_PERFIL_MM,
            facecolor=estilos.COLOR_PERFIL,
            alpha=0.35,
            edgecolor=estilos.COLOR_PERFIL,
            linewidth=1.5,
            zorder=2,
        )
    )
    _dibujar_linea_de_corte(ax, -ancho_x / 2, ancho_x / 2, y_tope - ALTURA_STUB_PERFIL_MM * 0.08)


def _dibujar_linea_de_corte(ax, x_izquierda: float, x_derecha: float, y: float) -> None:
    """Línea en zigzag que indica que el elemento continúa más allá del
    dibujo (convención de dibujo técnico para elementos truncados)."""
    n = 7
    xs = np.linspace(x_izquierda, x_derecha, n)
    amplitud = (x_derecha - x_izquierda) / (n * 4) if x_derecha > x_izquierda else 1.0
    ys = [y + (amplitud if i % 2 else -amplitud) for i in range(n)]
    ax.plot(xs, ys, color=estilos.COLOR_PERFIL, linewidth=1.2, zorder=5)
