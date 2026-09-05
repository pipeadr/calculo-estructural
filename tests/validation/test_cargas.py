"""Pruebas de las validaciones relacionadas con las cargas.

Nota: el modelo Cargas fija las unidades por el nombre del campo (_kn /
_knm) y exige tipo float, así que no puede existir un objeto Cargas con
"unidades inválidas" — eso ya está garantizado en la Etapa 1. El caso de
prueba equivalente en esta etapa es que no se haya documentado la
convención de signos o el tipo de combinación de carga.
"""

from __future__ import annotations

from calculo_estructural.models import TipoCombinacionCarga
from calculo_estructural.validation import EstadoValidacion
from calculo_estructural.validation.cargas import (
    validar_convencion_signos,
    validar_tipo_combinacion,
    validar_unidades_y_valores_numericos,
)


def test_unidades_y_valores_numericos_siempre_es_ok(cargas_ejemplo):
    resultado = validar_unidades_y_valores_numericos(cargas_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


# --- Caso 9: "cargas con unidades inválidas" -> convención/combinación
# no especificada (ver nota del módulo) ----------------------------------


def test_convencion_signos_vacia_es_advertencia(cargas_ejemplo):
    resultado = validar_convencion_signos(cargas_ejemplo)
    assert resultado.estado == EstadoValidacion.ADVERTENCIA


def test_convencion_signos_definida_es_ok(cargas_ejemplo):
    cargas_con_convencion = cargas_ejemplo.model_copy(
        update={"convencion_signos": "Axial positivo = compresión"}
    )
    resultado = validar_convencion_signos(cargas_con_convencion)
    assert resultado.estado == EstadoValidacion.OK


def test_tipo_combinacion_no_especificada_es_advertencia(cargas_ejemplo):
    resultado = validar_tipo_combinacion(cargas_ejemplo)
    assert resultado.estado == EstadoValidacion.ADVERTENCIA


def test_tipo_combinacion_definida_es_ok(cargas_ejemplo):
    cargas_factorizadas = cargas_ejemplo.model_copy(update={"tipo_combinacion": TipoCombinacionCarga.FACTORIZADA})
    resultado = validar_tipo_combinacion(cargas_factorizadas)
    assert resultado.estado == EstadoValidacion.OK
