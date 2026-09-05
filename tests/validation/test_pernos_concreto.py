"""Pruebas de las validaciones cruzadas entre pernos y elemento de concreto."""

from __future__ import annotations

from calculo_estructural.models import PosicionPerno
from calculo_estructural.validation import EstadoValidacion
from calculo_estructural.validation.pernos_concreto import (
    validar_embebido_dentro_de_altura,
    validar_pernos_dentro_del_concreto,
)


def test_pernos_dentro_del_concreto_es_ok(pernos_ejemplo, elemento_concreto_ejemplo):
    resultado = validar_pernos_dentro_del_concreto(pernos_ejemplo, elemento_concreto_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


# --- Caso 6: perno fuera del concreto -----------------------------------


def test_perno_fuera_del_concreto_es_error(pernos_ejemplo, elemento_concreto_ejemplo):
    pernos_fuera = pernos_ejemplo.model_copy(
        update={"posiciones": [PosicionPerno(x_mm=100000, y_mm=0), *pernos_ejemplo.posiciones[1:]]}
    )
    resultado = validar_pernos_dentro_del_concreto(pernos_fuera, elemento_concreto_ejemplo)
    assert resultado.estado == EstadoValidacion.ERROR
    assert resultado.datos["pernos_fuera"][0]["indice"] == 0


# --- Caso 7: profundidad de embebido inválida (cruzada con la altura) --


def test_embebido_dentro_de_altura_es_ok(pernos_ejemplo, elemento_concreto_ejemplo):
    resultado = validar_embebido_dentro_de_altura(pernos_ejemplo, elemento_concreto_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_embebido_mayor_que_altura_del_concreto_es_error(pernos_ejemplo, elemento_concreto_ejemplo):
    pernos_muy_profundos = pernos_ejemplo.model_copy(update={"profundidad_embebido_mm": 99999})
    resultado = validar_embebido_dentro_de_altura(pernos_muy_profundos, elemento_concreto_ejemplo)
    assert resultado.estado == EstadoValidacion.ERROR
