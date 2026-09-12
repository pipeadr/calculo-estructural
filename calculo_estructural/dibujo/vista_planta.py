"""Vista en planta de la conexión: contorno de la placa, perfil,
perforaciones, pernos, ejes, cotas principales y cargas.

Sistema de referencia (el mismo que ya usan ``Perforacion`` y
``PosicionPerno``): origen en el centroide de la placa, X a lo largo de
``largo_mm``, Y a lo largo de ``ancho_mm``. Para las cargas se extiende
con un eje Z perpendicular a la placa, positivo hacia el perfil
(alejándose del concreto) — esta vista mira en la dirección -Z (desde
arriba), por eso Z solo aparece de forma indirecta.

Convención de dibujo de las cargas (es notación matemática de diagrama de
cuerpo libre, NO una interpretación de ingeniería — compresión/tracción,
etc. queda a criterio de ``Cargas.convencion_signos``, ya existente):

- Cortante X / Cortante Y: flecha en el plano, apuntando en el sentido
  positivo o negativo de cada eje según el signo del valor.
- Momento Z: flecha curva; antihorario = positivo (regla de la mano
  derecha, con Z saliendo hacia el observador).
- Axial, Momento X y Momento Y: son perpendiculares a este plano — se
  marcan con la notación estándar de vector saliente (símbolo ⊙,
  positivo) o entrante (símbolo ⊗, negativo) junto a su valor.

Todo elemento es opcional: si la sección correspondiente del proyecto es
``None``, esa parte simplemente no se dibuja (no se lanza ningún error).
"""

from __future__ import annotations

from matplotlib.figure import Figure
from matplotlib.patches import Circle, Polygon, Rectangle

from ..calculos import contorno_perfil_ih
from ..models import (
    Cargas,
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilMetalico,
    PerfilRectangular,
    Pernos,
    PlacaBase,
    Proyecto,
)
from . import estilos


def dibujar_vista_planta(proyecto: Proyecto) -> Figure:
    """Genera la ``Figure`` de la vista en planta para el estado actual
    del proyecto."""
    fig = Figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.set_title("Vista en planta")

    placa = proyecto.placa_base
    if placa is None:
        ax.text(0.5, 0.5, "Falta definir la placa base", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return fig

    medio_largo = placa.largo_mm / 2
    medio_ancho = placa.ancho_mm / 2

    _dibujar_ejes(ax, medio_largo, medio_ancho)
    _dibujar_placa(ax, placa)
    if proyecto.perfil_metalico is not None:
        _dibujar_perfil(ax, proyecto.perfil_metalico)
    _dibujar_perforaciones(ax, placa)
    if proyecto.pernos is not None:
        _dibujar_pernos(ax, proyecto.pernos)
    if proyecto.cargas is not None:
        escala = min(medio_largo, medio_ancho) * 0.6
        _dibujar_cargas(ax, proyecto.cargas, escala)
        fig.text(
            0.02,
            0.02,
            "Cargas: flecha = sentido del signo (no a escala). "
            "⊙ saliente (+) / ⊗ entrante (−) = fuera del plano. "
            "Curva antihoraria = momento positivo.",
            fontsize=7,
            color=estilos.COLOR_CARGA,
        )

    margen = max(placa.largo_mm, placa.ancho_mm) * 0.3
    ax.set_xlim(-medio_largo - margen, medio_largo + margen)
    ax.set_ylim(-medio_ancho - margen, medio_ancho + margen)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    return fig


def _dibujar_ejes(ax, medio_largo: float, medio_ancho: float) -> None:
    ax.axhline(0, color=estilos.COLOR_EJE, linestyle="--", linewidth=0.8, zorder=0)
    ax.axvline(0, color=estilos.COLOR_EJE, linestyle="--", linewidth=0.8, zorder=0)
    ax.text(medio_largo * 1.15, 0, "X", color=estilos.COLOR_EJE, fontsize=9, va="center")
    ax.text(0, medio_ancho * 1.15, "Y", color=estilos.COLOR_EJE, fontsize=9, ha="center")


def _dibujar_placa(ax, placa: PlacaBase) -> None:
    medio_largo = placa.largo_mm / 2
    medio_ancho = placa.ancho_mm / 2
    ax.add_patch(
        Rectangle(
            (-medio_largo, -medio_ancho),
            placa.largo_mm,
            placa.ancho_mm,
            facecolor="none",
            edgecolor=estilos.COLOR_PLACA,
            linewidth=1.8,
            zorder=1,
        )
    )
    estilos.dibujar_cota(
        ax,
        (-medio_largo, -medio_ancho - 20),
        (medio_largo, -medio_ancho - 20),
        f"{placa.largo_mm:g} mm",
    )
    estilos.dibujar_cota(
        ax,
        (medio_largo + 20, -medio_ancho),
        (medio_largo + 20, medio_ancho),
        f"{placa.ancho_mm:g} mm",
    )


def _dibujar_perfil(ax, perfil: PerfilMetalico) -> None:
    if isinstance(perfil, PerfilRectangular):
        _dibujar_rectangulo_con_hueco(ax, perfil.b_mm, perfil.h_mm, perfil.es_hueco, perfil.espesor_pared_mm)
    elif isinstance(perfil, PerfilCuadrado):
        _dibujar_rectangulo_con_hueco(ax, perfil.lado_mm, perfil.lado_mm, perfil.es_hueco, perfil.espesor_pared_mm)
    elif isinstance(perfil, PerfilCircular):
        _dibujar_circulo_con_hueco(ax, perfil.diametro_mm, perfil.es_hueco, perfil.espesor_pared_mm)
    elif isinstance(perfil, (PerfilI, PerfilH)):
        ax.add_patch(
            Polygon(
                contorno_perfil_ih(perfil),
                closed=True,
                facecolor=estilos.COLOR_PERFIL,
                alpha=0.35,
                edgecolor=estilos.COLOR_PERFIL,
                linewidth=1.5,
                zorder=2,
            )
        )


def _dibujar_rectangulo_con_hueco(ax, ancho: float, alto: float, es_hueco: bool, espesor_pared_mm: float | None) -> None:
    ax.add_patch(
        Rectangle(
            (-ancho / 2, -alto / 2),
            ancho,
            alto,
            facecolor=estilos.COLOR_PERFIL,
            alpha=0.35,
            edgecolor=estilos.COLOR_PERFIL,
            linewidth=1.5,
            zorder=2,
        )
    )
    if es_hueco and espesor_pared_mm and espesor_pared_mm * 2 < min(ancho, alto):
        t = espesor_pared_mm
        ax.add_patch(
            Rectangle(
                (-ancho / 2 + t, -alto / 2 + t),
                ancho - 2 * t,
                alto - 2 * t,
                facecolor="white",
                edgecolor=estilos.COLOR_PERFIL,
                linewidth=1.0,
                zorder=3,
            )
        )


def _dibujar_circulo_con_hueco(ax, diametro: float, es_hueco: bool, espesor_pared_mm: float | None) -> None:
    radio = diametro / 2
    ax.add_patch(
        Circle((0, 0), radio, facecolor=estilos.COLOR_PERFIL, alpha=0.35, edgecolor=estilos.COLOR_PERFIL, linewidth=1.5, zorder=2)
    )
    if es_hueco and espesor_pared_mm and espesor_pared_mm < radio:
        ax.add_patch(
            Circle((0, 0), radio - espesor_pared_mm, facecolor="white", edgecolor=estilos.COLOR_PERFIL, linewidth=1.0, zorder=3)
        )


def _dibujar_perforaciones(ax, placa: PlacaBase) -> None:
    radio = placa.diametro_perforacion_mm / 2
    for perforacion in placa.perforaciones:
        ax.add_patch(
            Circle(
                (perforacion.x_mm, perforacion.y_mm),
                radio,
                facecolor=estilos.COLOR_PERFORACION,
                edgecolor=estilos.COLOR_PERFORACION_BORDE,
                linewidth=1.0,
                zorder=4,
            )
        )


def _dibujar_pernos(ax, pernos: Pernos) -> None:
    radio = pernos.diametro_mm / 2
    for posicion in pernos.posiciones:
        ax.add_patch(
            Circle(
                (posicion.x_mm, posicion.y_mm),
                radio,
                facecolor=estilos.COLOR_PERNO,
                edgecolor="black",
                linewidth=0.8,
                zorder=5,
            )
        )


def _dibujar_cargas(ax, cargas: Cargas, escala: float) -> None:
    origen = (0.0, 0.0)

    if cargas.cortante_x_kn != 0:
        dx = escala if cargas.cortante_x_kn > 0 else -escala
        estilos.dibujar_flecha(ax, origen, (dx, 0.0), f"Vx={cargas.cortante_x_kn:g} kN")
    if cargas.cortante_y_kn != 0:
        dy = escala if cargas.cortante_y_kn > 0 else -escala
        estilos.dibujar_flecha(ax, origen, (0.0, dy), f"Vy={cargas.cortante_y_kn:g} kN")
    if cargas.momento_z_knm != 0:
        estilos.dibujar_momento_curvo(
            ax, origen, cargas.momento_z_knm > 0, f"Mz={cargas.momento_z_knm:g} kN·m", radio=escala * 0.55
        )
    if cargas.axial_kn != 0:
        estilos.dibujar_vector_fuera_de_plano(
            ax, (escala * 0.85, escala * 0.85), cargas.axial_kn > 0, f"N={cargas.axial_kn:g} kN", radio=escala * 0.16
        )
    if cargas.momento_x_knm != 0:
        estilos.dibujar_vector_fuera_de_plano(
            ax,
            (-escala * 0.85, escala * 0.85),
            cargas.momento_x_knm > 0,
            f"Mx={cargas.momento_x_knm:g} kN·m",
            radio=escala * 0.16,
        )
    if cargas.momento_y_knm != 0:
        estilos.dibujar_vector_fuera_de_plano(
            ax,
            (-escala * 0.85, -escala * 0.85),
            cargas.momento_y_knm > 0,
            f"My={cargas.momento_y_knm:g} kN·m",
            radio=escala * 0.16,
        )
