"""Pruebas de la estructura común ResultadoValidacion."""

from __future__ import annotations

from calculo_estructural.validation import Componente, EstadoValidacion, ResultadoValidacion


def test_resultado_validacion_se_construye_con_valores_por_defecto():
    resultado = ResultadoValidacion(codigo="X", nombre="Prueba", estado=EstadoValidacion.OK, mensaje="ok")
    assert resultado.componentes == []
    assert resultado.datos == {}


def test_es_bloqueante_solo_en_estado_error():
    for estado in EstadoValidacion:
        resultado = ResultadoValidacion(codigo="X", nombre="n", estado=estado, mensaje="m")
        assert resultado.es_bloqueante == (estado == EstadoValidacion.ERROR)


def test_componente_incluye_las_seis_secciones_y_proyecto():
    nombres = {c.value for c in Componente}
    assert nombres == {
        "proyecto",
        "placa_base",
        "perfil_metalico",
        "elemento_concreto",
        "pernos",
        "soldadura",
        "cargas",
    }
