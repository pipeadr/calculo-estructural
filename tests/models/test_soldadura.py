"""Pruebas del modelo Soldadura."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from calculo_estructural.models import Soldadura, TipoSoldadura


def _soldadura_valida(**overrides) -> dict:
    datos = dict(
        tipo_soldadura=TipoSoldadura.FILETE,
        simbolo="Filete continuo, ambos lados",
        espesor_mm=8,
        longitud_mm=200,
    )
    datos.update(overrides)
    return datos


def test_soldadura_valida_se_construye_correctamente():
    soldadura = Soldadura(**_soldadura_valida())
    assert soldadura.espesor_mm == 8


@pytest.mark.parametrize("campo", ["espesor_mm", "longitud_mm"])
def test_soldadura_rechaza_valores_no_positivos(campo):
    with pytest.raises(ValidationError):
        Soldadura(**_soldadura_valida(**{campo: 0}))


def test_soldadura_simbolo_vacio_es_rechazado():
    with pytest.raises(ValidationError):
        Soldadura(**_soldadura_valida(simbolo=""))


def test_soldadura_tipo_otro_requiere_texto():
    with pytest.raises(ValidationError):
        Soldadura(**_soldadura_valida(tipo_soldadura=TipoSoldadura.OTRO))


def test_soldadura_tipo_otro_con_texto_es_valido():
    soldadura = Soldadura(
        **_soldadura_valida(
            tipo_soldadura=TipoSoldadura.OTRO,
            tipo_soldadura_otro="Soldadura de tapón",
        )
    )
    assert soldadura.tipo_soldadura_otro == "Soldadura de tapón"
