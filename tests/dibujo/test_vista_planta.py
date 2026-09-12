"""Pruebas de dibujo.vista_planta."""

from __future__ import annotations

from datetime import datetime

import pytest
from matplotlib.patches import Circle, Polygon

from calculo_estructural.dibujo import dibujar_vista_planta
from calculo_estructural.models import MetadatosProyecto, PerfilI, Proyecto, TipoAcero


def test_vista_planta_sin_placa_no_lanza_error():
    ahora = datetime.now()
    proyecto = Proyecto(metadatos=MetadatosProyecto(nombre="Vacío", fecha_creacion=ahora, fecha_modificacion=ahora))

    figura = dibujar_vista_planta(proyecto)

    assert figura is not None
    assert len(figura.axes) == 1


def test_vista_planta_con_solo_placa_no_lanza_error(placa_base_ejemplo):
    ahora = datetime.now()
    proyecto = Proyecto(
        metadatos=MetadatosProyecto(nombre="Solo placa", fecha_creacion=ahora, fecha_modificacion=ahora),
        placa_base=placa_base_ejemplo,
    )

    figura = dibujar_vista_planta(proyecto)

    assert figura is not None


def test_vista_planta_dibuja_una_perforacion_por_cada_una_del_proyecto(proyecto_ejemplo):
    figura = dibujar_vista_planta(proyecto_ejemplo)
    ax = figura.axes[0]

    radio_esperado = proyecto_ejemplo.placa_base.diametro_perforacion_mm / 2
    circulos_perforacion = [
        p for p in ax.patches if isinstance(p, Circle) and p.radius == pytest.approx(radio_esperado)
    ]

    assert len(circulos_perforacion) == len(proyecto_ejemplo.placa_base.perforaciones)


def test_vista_planta_dibuja_un_perno_por_cada_uno_del_proyecto(proyecto_ejemplo):
    figura = dibujar_vista_planta(proyecto_ejemplo)
    ax = figura.axes[0]

    radio_esperado = proyecto_ejemplo.pernos.diametro_mm / 2
    circulos_perno = [p for p in ax.patches if isinstance(p, Circle) and p.radius == pytest.approx(radio_esperado)]

    assert len(circulos_perno) == len(proyecto_ejemplo.pernos.posiciones)


def test_vista_planta_dibuja_el_contorno_de_un_perfil_ih(placa_base_ejemplo):
    ahora = datetime.now()
    proyecto = Proyecto(
        metadatos=MetadatosProyecto(nombre="Con perfil I", fecha_creacion=ahora, fecha_modificacion=ahora),
        placa_base=placa_base_ejemplo,
        perfil_metalico=PerfilI(
            tipo_acero=TipoAcero.A992,
            fy_mpa=345,
            peralte_mm=300,
            ancho_ala_mm=150,
            espesor_ala_mm=12,
            espesor_alma_mm=8,
        ),
    )

    figura = dibujar_vista_planta(proyecto)
    ax = figura.axes[0]

    assert any(isinstance(p, Polygon) for p in ax.patches)


def test_vista_planta_con_proyecto_completo_no_lanza_error(proyecto_ejemplo):
    figura = dibujar_vista_planta(proyecto_ejemplo)
    assert figura is not None
