"""Fixtures compartidas por toda la suite de pruebas.

Construyen instancias válidas de cada entidad para que las pruebas de
``models``, y en etapas futuras las de ``validation``, ``calculos`` y
``persistencia``, no tengan que repetir los mismos datos de ejemplo.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from calculo_estructural.models import (
    Cargas,
    ElementoConcreto,
    MetadatosProyecto,
    Perforacion,
    PerfilRectangular,
    Pernos,
    PlacaBase,
    PosicionPerno,
    Proyecto,
    Soldadura,
    TipoAcero,
    TipoElementoConcreto,
    TipoGradoPerno,
    TipoSoldadura,
)


@pytest.fixture
def placa_base_ejemplo() -> PlacaBase:
    return PlacaBase(
        largo_mm=400,
        ancho_mm=400,
        espesor_mm=25,
        tipo_acero=TipoAcero.A36,
        fy_mpa=250,
        numero_perforaciones=4,
        diametro_perforacion_in=1.0,
        perforaciones=[
            Perforacion(x_mm=150, y_mm=150),
            Perforacion(x_mm=-150, y_mm=150),
            Perforacion(x_mm=-150, y_mm=-150),
            Perforacion(x_mm=150, y_mm=-150),
        ],
    )


@pytest.fixture
def perfil_metalico_ejemplo() -> PerfilRectangular:
    return PerfilRectangular(
        tipo_acero=TipoAcero.A500_GR_B,
        fy_mpa=317,
        b_mm=200,
        h_mm=200,
        es_hueco=True,
        espesor_pared_mm=8,
    )


@pytest.fixture
def elemento_concreto_ejemplo() -> ElementoConcreto:
    return ElementoConcreto(
        tipo_elemento=TipoElementoConcreto.PEDESTAL,
        largo_mm=600,
        ancho_mm=600,
        altura_mm=500,
        fc_mpa=28,
    )


@pytest.fixture
def pernos_ejemplo() -> Pernos:
    # diametro_in=0.875 (7/8") + holgura estándar de 1/8" coincide
    # exactamente con diametro_perforacion_in=1.0 de placa_base_ejemplo,
    # para que el proyecto de ejemplo pase también la validación cruzada
    # de compatibilidad de diámetro perno-perforación (Etapa 2) con OK.
    return Pernos(
        cantidad=4,
        diametro_in=0.875,
        longitud_mm=400,
        tipo_grado=TipoGradoPerno.F1554_GR36,
        profundidad_embebido_mm=300,
        posiciones=[
            PosicionPerno(x_mm=150, y_mm=150),
            PosicionPerno(x_mm=-150, y_mm=150),
            PosicionPerno(x_mm=-150, y_mm=-150),
            PosicionPerno(x_mm=150, y_mm=-150),
        ],
    )


@pytest.fixture
def soldadura_ejemplo() -> Soldadura:
    return Soldadura(
        tipo_soldadura=TipoSoldadura.FILETE,
        simbolo="Filete continuo, ambos lados",
        espesor_mm=8,
        longitud_mm=200,
    )


@pytest.fixture
def cargas_ejemplo() -> Cargas:
    return Cargas(
        axial_kn=-150.0,
        cortante_x_kn=20.0,
        cortante_y_kn=-15.0,
        momento_x_knm=5.0,
        momento_y_knm=3.0,
        momento_z_knm=0.5,
    )


@pytest.fixture
def proyecto_ejemplo(
    placa_base_ejemplo: PlacaBase,
    perfil_metalico_ejemplo: PerfilRectangular,
    elemento_concreto_ejemplo: ElementoConcreto,
    pernos_ejemplo: Pernos,
    soldadura_ejemplo: Soldadura,
    cargas_ejemplo: Cargas,
) -> Proyecto:
    ahora = datetime(2026, 1, 1, 12, 0, 0)
    return Proyecto(
        metadatos=MetadatosProyecto(
            nombre="Proyecto de ejemplo",
            descripcion="Conexión de columna HSS a placa base",
            autor="Pruebas automáticas",
            fecha_creacion=ahora,
            fecha_modificacion=ahora,
        ),
        placa_base=placa_base_ejemplo,
        perfil_metalico=perfil_metalico_ejemplo,
        elemento_concreto=elemento_concreto_ejemplo,
        pernos=pernos_ejemplo,
        soldadura=soldadura_ejemplo,
        cargas=cargas_ejemplo,
    )
