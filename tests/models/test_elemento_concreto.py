"""Pruebas del modelo ElementoConcreto."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from calculo_estructural.models import ElementoConcreto, TipoElementoConcreto


def _concreto_valido(**overrides) -> dict:
    datos = dict(
        tipo_elemento=TipoElementoConcreto.PEDESTAL,
        largo_mm=600,
        ancho_mm=600,
        altura_mm=500,
        fc_mpa=28,
    )
    datos.update(overrides)
    return datos


def test_elemento_concreto_valido():
    elemento = ElementoConcreto(**_concreto_valido())
    assert elemento.fc_mpa == 28


@pytest.mark.parametrize("campo", ["largo_mm", "ancho_mm", "altura_mm", "fc_mpa"])
def test_elemento_concreto_rechaza_valores_no_positivos(campo):
    with pytest.raises(ValidationError):
        ElementoConcreto(**_concreto_valido(**{campo: 0}))


def test_elemento_concreto_tipo_otro_requiere_texto():
    with pytest.raises(ValidationError):
        ElementoConcreto(**_concreto_valido(tipo_elemento=TipoElementoConcreto.OTRO))


def test_elemento_concreto_tipo_otro_con_texto_es_valido():
    elemento = ElementoConcreto(
        **_concreto_valido(
            tipo_elemento=TipoElementoConcreto.OTRO,
            tipo_elemento_otro="Dado de anclaje",
        )
    )
    assert elemento.tipo_elemento_otro == "Dado de anclaje"
