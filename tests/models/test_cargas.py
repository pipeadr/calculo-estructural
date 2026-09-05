"""Pruebas del modelo Cargas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from calculo_estructural.models import Cargas


def test_cargas_admite_valores_positivos_y_negativos():
    cargas = Cargas(
        axial_kn=-150.0,
        cortante_x_kn=20.0,
        cortante_y_kn=-15.0,
        momento_x_knm=5.0,
        momento_y_knm=-3.0,
        momento_z_knm=0.0,
    )
    assert cargas.axial_kn == -150.0
    assert cargas.momento_z_knm == 0.0


def test_cargas_requiere_todos_los_campos():
    with pytest.raises(ValidationError):
        Cargas(axial_kn=-150.0, cortante_x_kn=20.0)


def test_cargas_rechaza_valores_no_numericos():
    with pytest.raises(ValidationError):
        Cargas(
            axial_kn="no es un número",
            cortante_x_kn=0,
            cortante_y_kn=0,
            momento_x_knm=0,
            momento_y_knm=0,
            momento_z_knm=0,
        )
