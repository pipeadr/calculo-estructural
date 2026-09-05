"""Pruebas del modelo raíz Proyecto, incluyendo el round-trip a través de
un dict (equivalente a lo que hará la capa de persistencia con JSON)."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from calculo_estructural.models import MetadatosProyecto, PerfilI, Proyecto


def _metadatos() -> MetadatosProyecto:
    ahora = datetime(2026, 1, 1, 12, 0)
    return MetadatosProyecto(
        nombre="Proyecto de prueba",
        fecha_creacion=ahora,
        fecha_modificacion=ahora,
    )


def test_proyecto_puede_crearse_solo_con_metadatos():
    proyecto = Proyecto(metadatos=_metadatos())
    assert proyecto.placa_base is None
    assert proyecto.perfil_metalico is None
    assert proyecto.version_formato == "1.0"


def test_proyecto_completo_round_trip_por_dict(proyecto_ejemplo: Proyecto):
    como_dict = proyecto_ejemplo.model_dump(mode="json")
    reconstruido = Proyecto.model_validate(como_dict)

    assert reconstruido == proyecto_ejemplo
    assert isinstance(
        reconstruido.perfil_metalico, type(proyecto_ejemplo.perfil_metalico)
    )


def test_proyecto_con_perfil_i_round_trip_por_dict():
    proyecto = Proyecto(
        metadatos=_metadatos(),
        perfil_metalico=PerfilI(
            tipo_acero="A992",
            fy_mpa=345,
            peralte_mm=300,
            ancho_ala_mm=150,
            espesor_ala_mm=12,
            espesor_alma_mm=8,
        ),
    )
    reconstruido = Proyecto.model_validate(proyecto.model_dump(mode="json"))
    assert isinstance(reconstruido.perfil_metalico, PerfilI)


def test_proyecto_rechaza_campos_desconocidos():
    with pytest.raises(ValidationError):
        Proyecto(metadatos=_metadatos(), campo_inventado=123)
