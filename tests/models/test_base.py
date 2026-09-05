"""Pruebas de las utilidades compartidas en calculo_estructural.models.base."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from calculo_estructural.models.base import (
    ProyectoBaseModel,
    PuntoCoordenado,
    requerir_si,
)


def test_requerir_si_lanza_error_cuando_condicion_y_valor_vacio():
    with pytest.raises(ValueError, match="mensaje de prueba"):
        requerir_si(True, None, "mensaje de prueba")


def test_requerir_si_lanza_error_con_cadena_en_blanco():
    with pytest.raises(ValueError):
        requerir_si(True, "   ", "obligatorio")


def test_requerir_si_no_lanza_error_si_condicion_es_falsa():
    requerir_si(False, None, "no debería lanzar")


def test_requerir_si_no_lanza_error_si_valor_presente():
    requerir_si(True, "acero A36", "no debería lanzar")


def test_punto_coordenado_valores_correctos():
    punto = PuntoCoordenado(x_mm=10.5, y_mm=-3.2)
    assert punto.x_mm == 10.5
    assert punto.y_mm == -3.2


def test_extra_forbid_rechaza_campos_desconocidos():
    class _ModeloDePrueba(ProyectoBaseModel):
        campo: int

    with pytest.raises(ValidationError):
        _ModeloDePrueba(campo=1, campo_extra="no debería aceptarse")


def test_validate_assignment_revalida_al_reasignar():
    class _ModeloDePrueba(ProyectoBaseModel):
        valor: int

    instancia = _ModeloDePrueba(valor=1)
    instancia.valor = 2
    assert instancia.valor == 2
