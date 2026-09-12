"""Pruebas de dibujo.seccion_transversal."""

from __future__ import annotations

from datetime import datetime

from calculo_estructural.dibujo import dibujar_seccion_transversal
from calculo_estructural.models import MetadatosProyecto, Proyecto


def test_seccion_sin_placa_no_lanza_error():
    ahora = datetime.now()
    proyecto = Proyecto(metadatos=MetadatosProyecto(nombre="Vacío", fecha_creacion=ahora, fecha_modificacion=ahora))

    figura = dibujar_seccion_transversal(proyecto)

    assert figura is not None
    assert len(figura.axes) == 1


def test_seccion_con_solo_placa_no_lanza_error(placa_base_ejemplo):
    ahora = datetime.now()
    proyecto = Proyecto(
        metadatos=MetadatosProyecto(nombre="Solo placa", fecha_creacion=ahora, fecha_modificacion=ahora),
        placa_base=placa_base_ejemplo,
    )

    figura = dibujar_seccion_transversal(proyecto)

    assert figura is not None


def test_seccion_con_proyecto_completo_dibuja_una_varilla_por_cada_x_distinta(proyecto_ejemplo):
    figura = dibujar_seccion_transversal(proyecto_ejemplo)
    ax = figura.axes[0]

    xs_distintas = {round(p.x_mm, 6) for p in proyecto_ejemplo.pernos.posiciones}
    lineas_verticales = [
        linea
        for linea in ax.get_lines()
        if len(set(linea.get_xdata())) == 1  # una línea vertical tiene la misma X en ambos extremos
    ]

    assert len(lineas_verticales) == len(xs_distintas)


def test_seccion_con_proyecto_completo_no_lanza_error(proyecto_ejemplo):
    figura = dibujar_seccion_transversal(proyecto_ejemplo)
    assert figura is not None
