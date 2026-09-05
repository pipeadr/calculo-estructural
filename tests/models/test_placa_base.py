"""Pruebas del modelo PlacaBase."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from calculo_estructural.models import Perforacion, PlacaBase, TipoAcero


def _placa_valida(**overrides) -> dict:
    datos = dict(
        largo_mm=400,
        ancho_mm=400,
        espesor_mm=25,
        tipo_acero=TipoAcero.A36,
        fy_mpa=250,
        numero_perforaciones=2,
        diametro_perforacion_in=1.0,
        perforaciones=[
            Perforacion(x_mm=100, y_mm=0),
            Perforacion(x_mm=-100, y_mm=0),
        ],
    )
    datos.update(overrides)
    return datos


def test_placa_base_valida_se_construye_correctamente():
    placa = PlacaBase(**_placa_valida())
    assert placa.largo_mm == 400
    assert len(placa.perforaciones) == 2


@pytest.mark.parametrize("campo", ["largo_mm", "ancho_mm", "espesor_mm", "fy_mpa"])
def test_placa_base_rechaza_dimensiones_no_positivas(campo):
    with pytest.raises(ValidationError):
        PlacaBase(**_placa_valida(**{campo: 0}))


def test_placa_base_diametro_perforacion_convertido_a_mm():
    placa = PlacaBase(**_placa_valida(diametro_perforacion_in=1.0))
    assert placa.diametro_perforacion_mm == pytest.approx(25.4)


def test_placa_base_tipo_acero_otro_requiere_texto():
    with pytest.raises(ValidationError):
        PlacaBase(**_placa_valida(tipo_acero=TipoAcero.OTRO))


def test_placa_base_tipo_acero_otro_con_texto_es_valido():
    placa = PlacaBase(
        **_placa_valida(tipo_acero=TipoAcero.OTRO, tipo_acero_otro="A588")
    )
    assert placa.tipo_acero_otro == "A588"


def test_placa_base_numero_perforaciones_debe_coincidir_con_la_lista():
    with pytest.raises(ValidationError):
        PlacaBase(**_placa_valida(numero_perforaciones=3))


def test_placa_base_revalida_al_reasignar_un_campo():
    placa = PlacaBase(**_placa_valida())
    with pytest.raises(ValidationError):
        placa.largo_mm = -10
