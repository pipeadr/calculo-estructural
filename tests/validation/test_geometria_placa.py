"""Pruebas de las validaciones cruzadas de geometría de la placa."""

from __future__ import annotations

from calculo_estructural.models import Perforacion, PosicionPerno
from calculo_estructural.validation import EstadoValidacion
from calculo_estructural.validation.geometria_placa import (
    validar,
    validar_perfil_dentro_de_placa,
    validar_perforaciones_dentro_de_placa,
    validar_perforaciones_sin_superposicion,
    validar_pernos_dentro_de_placa,
)


def test_perforaciones_dentro_de_placa_es_ok(placa_base_ejemplo):
    resultado = validar_perforaciones_dentro_de_placa(placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_perforacion_fuera_de_placa_es_error(placa_base_ejemplo):
    placa_con_hueco_afuera = placa_base_ejemplo.model_copy(
        update={"perforaciones": [Perforacion(x_mm=100000, y_mm=0), *placa_base_ejemplo.perforaciones[1:]]}
    )
    resultado = validar_perforaciones_dentro_de_placa(placa_con_hueco_afuera)
    assert resultado.estado == EstadoValidacion.ERROR


def test_perforaciones_sin_superposicion_es_ok(placa_base_ejemplo):
    resultado = validar_perforaciones_sin_superposicion(placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_perforaciones_superpuestas_es_error(placa_base_ejemplo):
    placa_superpuesta = placa_base_ejemplo.model_copy(
        update={
            "perforaciones": [
                Perforacion(x_mm=150, y_mm=150),
                Perforacion(x_mm=150.5, y_mm=150),
                *placa_base_ejemplo.perforaciones[2:],
            ]
        }
    )
    resultado = validar_perforaciones_sin_superposicion(placa_superpuesta)
    assert resultado.estado == EstadoValidacion.ERROR


# --- Caso 5: perfil fuera de la placa -----------------------------------


def test_perfil_dentro_de_placa_es_ok(placa_base_ejemplo, perfil_metalico_ejemplo):
    resultado = validar_perfil_dentro_de_placa(perfil_metalico_ejemplo, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_perfil_mas_grande_que_la_placa_es_error(placa_base_ejemplo, perfil_metalico_ejemplo):
    perfil_enorme = perfil_metalico_ejemplo.model_copy(update={"b_mm": 5000, "h_mm": 5000})
    resultado = validar_perfil_dentro_de_placa(perfil_enorme, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.ERROR


# --- Caso 3: perno fuera de la placa ------------------------------------


def test_pernos_dentro_de_placa_es_ok(placa_base_ejemplo, pernos_ejemplo):
    resultado = validar_pernos_dentro_de_placa(pernos_ejemplo, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_perno_fuera_de_placa_es_error(placa_base_ejemplo, pernos_ejemplo):
    pernos_fuera = pernos_ejemplo.model_copy(
        update={"posiciones": [PosicionPerno(x_mm=100000, y_mm=0), *pernos_ejemplo.posiciones[1:]]}
    )
    resultado = validar_pernos_dentro_de_placa(pernos_fuera, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.ERROR


# --- validar() agregador: NO_VERIFICADO cuando faltan secciones --------


def test_validar_reporta_no_verificado_si_falta_perfil_y_pernos(placa_base_ejemplo):
    resultados = validar(placa_base_ejemplo, perfil=None, pernos=None)
    estados = {r.codigo: r.estado for r in resultados}
    assert estados["PERFIL_DENTRO_DE_PLACA"] == EstadoValidacion.NO_VERIFICADO
    assert estados["PERNOS_DENTRO_DE_PLACA"] == EstadoValidacion.NO_VERIFICADO
