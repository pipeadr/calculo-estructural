"""Pruebas de los widgets reutilizables de ui.widgets."""

from __future__ import annotations

import pytest
from matplotlib.figure import Figure

from calculo_estructural.ui.widgets import LienzoMatplotlib, PanelValidaciones, TablaCoordenadas
from calculo_estructural.validation import Componente, EstadoValidacion, ResultadoValidacion

# --- LienzoMatplotlib ----------------------------------------------------


def test_lienzo_matplotlib_muestra_una_figura(qapp):
    lienzo = LienzoMatplotlib()
    figura = Figure()
    figura.add_subplot(111).plot([0, 1], [0, 1])

    lienzo.mostrar_figura(figura)

    assert lienzo.canvas.figure is figura


def test_lienzo_matplotlib_reemplaza_la_figura_anterior(qapp):
    lienzo = LienzoMatplotlib()
    lienzo.mostrar_figura(Figure())
    segunda_figura = Figure()

    lienzo.mostrar_figura(segunda_figura)

    assert lienzo.canvas.figure is segunda_figura


# --- TablaCoordenadas -----------------------------------------------------


def test_tabla_coordenadas_agregar_y_obtener_puntos(qapp):
    tabla = TablaCoordenadas()
    cambios = []
    tabla.puntos_cambiados.connect(lambda: cambios.append(True))

    tabla.cargar_puntos([(100.0, 50.0), (-100.0, 50.0)])

    assert tabla.cantidad() == 2
    assert tabla.obtener_puntos() == [(100.0, 50.0), (-100.0, 50.0)]
    assert cambios == []  # cargar_puntos es una recarga, no una edición del usuario


def test_tabla_coordenadas_agregar_fila_dispara_la_senal(qapp):
    tabla = TablaCoordenadas()
    cambios = []
    tabla.puntos_cambiados.connect(lambda: cambios.append(True))

    tabla._agregar_fila()

    assert tabla.cantidad() == 1
    assert len(cambios) == 1


def test_tabla_coordenadas_quitar_filas_seleccionadas(qapp):
    tabla = TablaCoordenadas()
    tabla.cargar_puntos([(1.0, 1.0), (2.0, 2.0), (3.0, 3.0)])
    tabla._tabla.selectRow(1)

    tabla._quitar_filas_seleccionadas()

    assert tabla.obtener_puntos() == [(1.0, 1.0), (3.0, 3.0)]


def test_tabla_coordenadas_texto_invalido_lanza_value_error(qapp):
    tabla = TablaCoordenadas()
    tabla.cargar_puntos([(0.0, 0.0)])
    tabla._tabla.item(0, 0).setText("no-es-un-numero")

    with pytest.raises(ValueError):
        tabla.obtener_puntos()


# --- PanelValidaciones -----------------------------------------------------


def test_panel_validaciones_muestra_una_fila_por_resultado(qapp):
    panel = PanelValidaciones()
    resultados = [
        ResultadoValidacion(
            codigo="X",
            nombre="Prueba",
            estado=EstadoValidacion.ERROR,
            mensaje="Algo falló",
            componentes=[Componente.PERNOS],
        ),
        ResultadoValidacion(codigo="Y", nombre="Otra", estado=EstadoValidacion.OK, mensaje="Todo bien"),
    ]

    panel.actualizar(resultados)

    assert panel.cantidad_filas() == 2
    assert panel.texto_de(0, 2) == "X"
    assert panel.texto_de(0, 3) == "Algo falló"
    assert panel.texto_de(1, 0) == "OK"


def test_panel_validaciones_resumen_por_estado(qapp):
    panel = PanelValidaciones()
    resultados = [
        ResultadoValidacion(codigo="A", nombre="a", estado=EstadoValidacion.ERROR, mensaje="m"),
        ResultadoValidacion(codigo="B", nombre="b", estado=EstadoValidacion.ADVERTENCIA, mensaje="m"),
        ResultadoValidacion(codigo="C", nombre="c", estado=EstadoValidacion.ADVERTENCIA, mensaje="m"),
        ResultadoValidacion(codigo="D", nombre="d", estado=EstadoValidacion.NO_VERIFICADO, mensaje="m"),
    ]

    resumen = panel.resumen_por_estado(resultados)

    assert resumen == "1 error(es) · 2 advertencia(s) · 1 sin verificar"
