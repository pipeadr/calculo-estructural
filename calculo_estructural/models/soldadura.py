"""Modelo de datos de la soldadura."""

from __future__ import annotations

from pydantic import Field, model_validator

from .base import ProyectoBaseModel, requerir_si
from .enums import TipoSoldadura


class Soldadura(ProyectoBaseModel):
    """Datos de la soldadura entre el perfil metálico y la placa base.

    ``simbolo`` es una anotación de texto libre (p. ej. "Filete continuo,
    ambos lados"). En esta fase no se dibuja el símbolo AWS real, solo se
    registra como referencia descriptiva.
    """

    tipo_soldadura: TipoSoldadura
    tipo_soldadura_otro: str | None = Field(
        default=None, description="Obligatorio si tipo_soldadura == OTRO"
    )
    simbolo: str = Field(min_length=1, description="Anotación/símbolo de la soldadura")
    espesor_mm: float = Field(gt=0, description="Tamaño de garganta/pata en mm")
    longitud_mm: float = Field(gt=0, description="Longitud de la soldadura en mm")

    @model_validator(mode="after")
    def _validar_tipo_soldadura_otro(self) -> "Soldadura":
        requerir_si(
            self.tipo_soldadura == TipoSoldadura.OTRO,
            self.tipo_soldadura_otro,
            "tipo_soldadura_otro es obligatorio cuando tipo_soldadura es OTRO",
        )
        return self
