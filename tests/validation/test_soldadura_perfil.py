"""Pruebas de las validaciones cruzadas entre soldadura y perfil metálico."""

from __future__ import annotations

from calculo_estructural.validation import EstadoValidacion
from calculo_estructural.validation.soldadura_perfil import (
    validar_espesor_vs_espesores_conectados,
    validar_longitud_vs_perimetro,
)


def test_longitud_de_soldadura_dentro_del_perimetro_es_ok(soldadura_ejemplo, perfil_metalico_ejemplo):
    resultado = validar_longitud_vs_perimetro(soldadura_ejemplo, perfil_metalico_ejemplo)
    assert resultado.estado == EstadoValidacion.OK


def test_longitud_de_soldadura_mayor_al_perimetro_es_advertencia(soldadura_ejemplo, perfil_metalico_ejemplo):
    soldadura_larga = soldadura_ejemplo.model_copy(update={"longitud_mm": 999999})
    resultado = validar_longitud_vs_perimetro(soldadura_larga, perfil_metalico_ejemplo)
    assert resultado.estado == EstadoValidacion.ADVERTENCIA


# --- Caso 8: soldadura con espesor "inválido" ---------------------------
# El espesor > 0 ya lo garantiza el modelo Soldadura (Etapa 1). Lo que
# pide esta etapa y todavía depende de un criterio normativo no definido
# (espesor máximo de filete según piezas conectadas) se deja marcado
# explícitamente como pendiente, no se inventa un límite:


def test_espesor_maximo_queda_marcado_como_no_verificado():
    resultado = validar_espesor_vs_espesores_conectados()
    assert resultado.estado == EstadoValidacion.NO_VERIFICADO
