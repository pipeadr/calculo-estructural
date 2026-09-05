"""Modelo de datos del elemento de concreto que recibe la placa base."""

from __future__ import annotations

from pydantic import Field, model_validator

from .base import ProyectoBaseModel, requerir_si
from .enums import TipoElementoConcreto


class ElementoConcreto(ProyectoBaseModel):
    """Datos geométricos y de material del elemento de concreto (zapata,
    pedestal, muro, losa, etc.) sobre el que se apoya la placa base."""

    tipo_elemento: TipoElementoConcreto
    tipo_elemento_otro: str | None = Field(
        default=None, description="Obligatorio si tipo_elemento == OTRO"
    )

    largo_mm: float = Field(gt=0, description="Largo del elemento en mm")
    ancho_mm: float = Field(gt=0, description="Ancho del elemento en mm")
    altura_mm: float = Field(
        gt=0, description="Altura o espesor del elemento en mm"
    )

    fc_mpa: float = Field(gt=0, description="Resistencia f'c del concreto en MPa")

    @model_validator(mode="after")
    def _validar_tipo_elemento_otro(self) -> "ElementoConcreto":
        requerir_si(
            self.tipo_elemento == TipoElementoConcreto.OTRO,
            self.tipo_elemento_otro,
            "tipo_elemento_otro es obligatorio cuando tipo_elemento es OTRO",
        )
        return self
