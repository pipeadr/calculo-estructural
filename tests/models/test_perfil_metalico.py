"""Pruebas de los modelos de perfil metálico y su unión discriminada."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from calculo_estructural.models import (
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilMetalico,
    PerfilRectangular,
    TipoAcero,
    TipoSeccionPerfil,
)

_ACERO = dict(tipo_acero=TipoAcero.A992, fy_mpa=345)


def test_perfil_rectangular_macizo_valido():
    perfil = PerfilRectangular(b_mm=200, h_mm=300, **_ACERO)
    assert perfil.tipo_seccion == TipoSeccionPerfil.RECTANGULAR
    assert perfil.es_hueco is False


def test_perfil_rectangular_hueco_requiere_espesor_pared():
    with pytest.raises(ValidationError):
        PerfilRectangular(b_mm=200, h_mm=300, es_hueco=True, **_ACERO)


def test_perfil_rectangular_hueco_con_espesor_pared_es_valido():
    perfil = PerfilRectangular(
        b_mm=200, h_mm=300, es_hueco=True, espesor_pared_mm=8, **_ACERO
    )
    assert perfil.espesor_pared_mm == 8


def test_perfil_cuadrado_valido():
    perfil = PerfilCuadrado(lado_mm=250, **_ACERO)
    assert perfil.tipo_seccion == TipoSeccionPerfil.CUADRADA


def test_perfil_circular_valido():
    perfil = PerfilCircular(diametro_mm=323.9, **_ACERO)
    assert perfil.tipo_seccion == TipoSeccionPerfil.CIRCULAR


def test_perfil_i_valido():
    perfil = PerfilI(
        peralte_mm=300,
        ancho_ala_mm=150,
        espesor_ala_mm=12,
        espesor_alma_mm=8,
        **_ACERO,
    )
    assert perfil.tipo_seccion == TipoSeccionPerfil.I


def test_perfil_h_valido():
    perfil = PerfilH(
        peralte_mm=300,
        ancho_ala_mm=300,
        espesor_ala_mm=15,
        espesor_alma_mm=10,
        **_ACERO,
    )
    assert perfil.tipo_seccion == TipoSeccionPerfil.H


def test_perfil_rechaza_fy_no_positivo():
    with pytest.raises(ValidationError):
        PerfilCuadrado(lado_mm=250, tipo_acero=TipoAcero.A992, fy_mpa=0)


def test_perfil_tipo_acero_otro_requiere_texto():
    with pytest.raises(ValidationError):
        PerfilCuadrado(lado_mm=250, tipo_acero=TipoAcero.OTRO, fy_mpa=250)


def test_union_discriminada_resuelve_la_clase_correcta_desde_un_dict():
    adaptador = TypeAdapter(PerfilMetalico)

    perfil_i = adaptador.validate_python(
        {
            "tipo_seccion": "I",
            "tipo_acero": "A992",
            "fy_mpa": 345,
            "peralte_mm": 300,
            "ancho_ala_mm": 150,
            "espesor_ala_mm": 12,
            "espesor_alma_mm": 8,
        }
    )
    assert isinstance(perfil_i, PerfilI)

    perfil_rect = adaptador.validate_python(
        {
            "tipo_seccion": "rectangular",
            "tipo_acero": "A36",
            "fy_mpa": 250,
            "b_mm": 200,
            "h_mm": 300,
        }
    )
    assert isinstance(perfil_rect, PerfilRectangular)
