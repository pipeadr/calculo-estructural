"""Pruebas del modelo Pernos."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from calculo_estructural.models import Pernos, PosicionPerno, TipoGradoPerno


def _pernos_validos(**overrides) -> dict:
    datos = dict(
        cantidad=2,
        diametro_in=0.75,
        longitud_mm=400,
        tipo_grado=TipoGradoPerno.F1554_GR36,
        profundidad_embebido_mm=300,
        posiciones=[
            PosicionPerno(x_mm=100, y_mm=0),
            PosicionPerno(x_mm=-100, y_mm=0),
        ],
    )
    datos.update(overrides)
    return datos


def test_pernos_validos_se_construyen_correctamente():
    pernos = Pernos(**_pernos_validos())
    assert pernos.cantidad == 2
    assert len(pernos.posiciones) == 2


def test_pernos_diametro_convertido_a_mm():
    pernos = Pernos(**_pernos_validos(diametro_in=1.0))
    assert pernos.diametro_mm == pytest.approx(25.4)


def test_pernos_cantidad_debe_coincidir_con_posiciones():
    with pytest.raises(ValidationError):
        Pernos(**_pernos_validos(cantidad=4))


@pytest.mark.parametrize(
    "campo", ["diametro_in", "longitud_mm", "profundidad_embebido_mm"]
)
def test_pernos_rechaza_valores_no_positivos(campo):
    with pytest.raises(ValidationError):
        Pernos(**_pernos_validos(**{campo: 0}))


def test_pernos_cantidad_no_positiva_es_rechazada():
    with pytest.raises(ValidationError):
        Pernos(**_pernos_validos(cantidad=0, posiciones=[]))


def test_pernos_tipo_grado_otro_requiere_texto():
    with pytest.raises(ValidationError):
        Pernos(**_pernos_validos(tipo_grado=TipoGradoPerno.OTRO))


def test_pernos_tipo_grado_otro_con_texto_es_valido():
    pernos = Pernos(
        **_pernos_validos(
            tipo_grado=TipoGradoPerno.OTRO, tipo_grado_otro="ASTM A354 BC"
        )
    )
    assert pernos.tipo_grado_otro == "ASTM A354 BC"
