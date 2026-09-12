"""Pruebas de los cálculos geométricos básicos (sin fórmulas de resistencia)."""

from __future__ import annotations

import math

import pytest

from calculo_estructural.calculos import (
    bounding_box_perfil,
    contorno_perfil_ih,
    distancia_entre_puntos,
    perimetro_perfil,
)
from calculo_estructural.models import (
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilRectangular,
    TipoAcero,
)

_ACERO = dict(tipo_acero=TipoAcero.A992, fy_mpa=345)


def test_bounding_box_rectangular():
    perfil = PerfilRectangular(b_mm=200, h_mm=300, **_ACERO)
    assert bounding_box_perfil(perfil) == (200, 300)


def test_bounding_box_cuadrado():
    perfil = PerfilCuadrado(lado_mm=250, **_ACERO)
    assert bounding_box_perfil(perfil) == (250, 250)


def test_bounding_box_circular():
    perfil = PerfilCircular(diametro_mm=323.9, **_ACERO)
    assert bounding_box_perfil(perfil) == (323.9, 323.9)


def test_bounding_box_ih():
    perfil = PerfilI(peralte_mm=300, ancho_ala_mm=150, espesor_ala_mm=12, espesor_alma_mm=8, **_ACERO)
    assert bounding_box_perfil(perfil) == (150, 300)


def test_perimetro_rectangular():
    perfil = PerfilRectangular(b_mm=200, h_mm=300, **_ACERO)
    assert perimetro_perfil(perfil) == pytest.approx(2 * (200 + 300))


def test_perimetro_cuadrado():
    perfil = PerfilCuadrado(lado_mm=250, **_ACERO)
    assert perimetro_perfil(perfil) == pytest.approx(4 * 250)


def test_perimetro_circular():
    perfil = PerfilCircular(diametro_mm=100, **_ACERO)
    assert perimetro_perfil(perfil) == pytest.approx(math.pi * 100)


def test_perimetro_ih():
    perfil = PerfilH(peralte_mm=300, ancho_ala_mm=300, espesor_ala_mm=15, espesor_alma_mm=10, **_ACERO)
    assert perimetro_perfil(perfil) == pytest.approx(4 * 300 + 2 * 300 - 2 * 10)


def test_distancia_entre_puntos():
    assert distancia_entre_puntos((0, 0), (3, 4)) == pytest.approx(5.0)
    assert distancia_entre_puntos((10, 10), (10, 10)) == pytest.approx(0.0)


def test_contorno_perfil_ih_tiene_12_vertices():
    perfil = PerfilI(peralte_mm=300, ancho_ala_mm=150, espesor_ala_mm=12, espesor_alma_mm=8, **_ACERO)
    contorno = contorno_perfil_ih(perfil)
    assert len(contorno) == 12


def test_contorno_perfil_ih_encaja_en_su_bounding_box():
    perfil = PerfilH(peralte_mm=300, ancho_ala_mm=280, espesor_ala_mm=15, espesor_alma_mm=10, **_ACERO)
    contorno = contorno_perfil_ih(perfil)
    xs = [x for x, _ in contorno]
    ys = [y for _, y in contorno]
    ancho_x, ancho_y = bounding_box_perfil(perfil)
    assert max(xs) - min(xs) == pytest.approx(ancho_x)
    assert max(ys) - min(ys) == pytest.approx(ancho_y)


def test_contorno_perfil_ih_perimetro_coincide_con_perimetro_perfil():
    perfil = PerfilI(peralte_mm=400, ancho_ala_mm=200, espesor_ala_mm=16, espesor_alma_mm=9, **_ACERO)
    contorno = contorno_perfil_ih(perfil)
    n = len(contorno)
    perimetro_por_vertices = sum(
        distancia_entre_puntos(contorno[i], contorno[(i + 1) % n]) for i in range(n)
    )
    assert perimetro_por_vertices == pytest.approx(perimetro_perfil(perfil))
