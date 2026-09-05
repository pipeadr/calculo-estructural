"""Pruebas de las validaciones cruzadas entre pernos y perforaciones."""

from __future__ import annotations

from calculo_estructural.models import Perforacion, PosicionPerno
from calculo_estructural.validation import EstadoValidacion
from calculo_estructural.validation.pernos_perforaciones import (
    validar_cantidad,
    validar_correspondencia_posiciones,
    validar_diametro_compatible,
    validar_sin_duplicados,
)

# --- Caso 1: perno compatible con perforación -------------------------


def test_diametro_compatible_con_holgura_estandar_es_ok(placa_base_ejemplo, pernos_ejemplo):
    resultado = validar_diametro_compatible(pernos_ejemplo, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


# --- Caso 2: perno incompatible con perforación ------------------------


def test_perforacion_mas_chica_que_el_perno_es_error(placa_base_ejemplo, pernos_ejemplo):
    pernos_incompatibles = pernos_ejemplo.model_copy(update={"diametro_in": 2.0})
    resultado = validar_diametro_compatible(pernos_incompatibles, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.ERROR


def test_holgura_distinta_de_un_octavo_es_advertencia(placa_base_ejemplo, pernos_ejemplo):
    # placa_base_ejemplo tiene diametro_perforacion_in=1.0; con un perno
    # de 0.5" la holgura sería 0.5" (mayor que 1/8"): cabe, pero no es la
    # holgura estándar -> ADVERTENCIA, no ERROR.
    pernos_holgados = pernos_ejemplo.model_copy(update={"diametro_in": 0.5})
    resultado = validar_diametro_compatible(pernos_holgados, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.ADVERTENCIA


# --- Cantidad de pernos vs. perforaciones -------------------------------


def test_cantidad_coincidente_es_ok(placa_base_ejemplo, pernos_ejemplo):
    resultado = validar_cantidad(pernos_ejemplo, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_mas_pernos_que_perforaciones_es_error(placa_base_ejemplo, pernos_ejemplo):
    placa_con_menos_huecos = placa_base_ejemplo.model_copy(
        update={
            "numero_perforaciones": 2,
            "perforaciones": placa_base_ejemplo.perforaciones[:2],
        }
    )
    resultado = validar_cantidad(pernos_ejemplo, placa_con_menos_huecos)
    assert resultado.estado == EstadoValidacion.ERROR


def test_menos_pernos_que_perforaciones_es_advertencia(placa_base_ejemplo, pernos_ejemplo):
    pernos_de_menos = pernos_ejemplo.model_copy(
        update={"cantidad": 2, "posiciones": pernos_ejemplo.posiciones[:2]}
    )
    resultado = validar_cantidad(pernos_de_menos, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.ADVERTENCIA


# --- Correspondencia de coordenadas -------------------------------------


def test_correspondencia_exacta_es_ok(placa_base_ejemplo, pernos_ejemplo):
    resultado = validar_correspondencia_posiciones(pernos_ejemplo, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_perno_sin_perforacion_correspondiente_es_error(placa_base_ejemplo, pernos_ejemplo):
    pernos_desplazados = pernos_ejemplo.model_copy(
        update={"posiciones": [PosicionPerno(x_mm=9999, y_mm=9999), *pernos_ejemplo.posiciones[1:]]}
    )
    resultado = validar_correspondencia_posiciones(pernos_desplazados, placa_base_ejemplo)
    assert resultado.estado == EstadoValidacion.ERROR
    assert resultado.datos["pernos_sin_perforacion"][0]["indice"] == 0


# --- Caso 4: perforación duplicada / pernos duplicados ------------------


def test_perforaciones_duplicadas_es_error(placa_base_ejemplo, pernos_ejemplo):
    placa_duplicada = placa_base_ejemplo.model_copy(
        update={
            "perforaciones": [
                Perforacion(x_mm=150, y_mm=150),
                Perforacion(x_mm=150, y_mm=150),
                *placa_base_ejemplo.perforaciones[2:],
            ]
        }
    )
    resultados = validar_sin_duplicados(pernos_ejemplo, placa_duplicada)
    resultado_perforaciones = next(r for r in resultados if r.codigo == "PERFORACIONES_DUPLICADAS")
    assert resultado_perforaciones.estado == EstadoValidacion.ERROR


def test_sin_perforaciones_duplicadas_es_ok(placa_base_ejemplo, pernos_ejemplo):
    resultados = validar_sin_duplicados(pernos_ejemplo, placa_base_ejemplo)
    resultado_perforaciones = next(r for r in resultados if r.codigo == "PERFORACIONES_DUPLICADAS")
    assert resultado_perforaciones.estado == EstadoValidacion.OK


def test_pernos_duplicados_es_error(placa_base_ejemplo, pernos_ejemplo):
    pernos_duplicados = pernos_ejemplo.model_copy(
        update={
            "posiciones": [
                pernos_ejemplo.posiciones[0],
                pernos_ejemplo.posiciones[0],
                *pernos_ejemplo.posiciones[2:],
            ]
        }
    )
    resultados = validar_sin_duplicados(pernos_duplicados, placa_base_ejemplo)
    resultado_pernos = next(r for r in resultados if r.codigo == "PERNOS_DUPLICADOS")
    assert resultado_pernos.estado == EstadoValidacion.ERROR
