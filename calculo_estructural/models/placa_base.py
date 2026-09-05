"""Modelo de datos de la placa base."""

from __future__ import annotations

from pydantic import Field, model_validator

from .base import MM_POR_PULGADA, ProyectoBaseModel, PuntoCoordenado, requerir_si
from .enums import TipoAcero


class Perforacion(PuntoCoordenado):
    """Posición (x, y) en mm de una perforación de la placa, respecto al
    centroide de la placa base."""


class PlacaBase(ProyectoBaseModel):
    """Datos geométricos y de material de la placa base."""

    largo_mm: float = Field(gt=0, description="Largo de la placa en mm")
    ancho_mm: float = Field(gt=0, description="Ancho de la placa en mm")
    espesor_mm: float = Field(gt=0, description="Espesor de la placa en mm")

    tipo_acero: TipoAcero
    tipo_acero_otro: str | None = Field(
        default=None, description="Obligatorio si tipo_acero == OTRO"
    )
    fy_mpa: float = Field(gt=0, description="Esfuerzo de fluencia Fy en MPa")

    numero_perforaciones: int = Field(ge=0, description="Cantidad de perforaciones")
    diametro_perforacion_in: float = Field(
        gt=0, description="Diámetro de las perforaciones en pulgadas"
    )
    perforaciones: list[Perforacion] = Field(
        default_factory=list,
        description="Coordenadas (x, y) en mm de cada perforación",
    )

    @property
    def diametro_perforacion_mm(self) -> float:
        """Diámetro de perforación convertido a milímetros.

        No es un ``computed_field`` (no se serializa en el JSON del
        proyecto): se recalcula a partir de ``diametro_perforacion_in``
        cada vez que se consulta, para no duplicar el dato guardado y
        evitar que quede desactualizado si se edita el archivo a mano.
        """
        return self.diametro_perforacion_in * MM_POR_PULGADA

    @model_validator(mode="after")
    def _validar_consistencia(self) -> "PlacaBase":
        requerir_si(
            self.tipo_acero == TipoAcero.OTRO,
            self.tipo_acero_otro,
            "tipo_acero_otro es obligatorio cuando tipo_acero es OTRO",
        )
        if len(self.perforaciones) != self.numero_perforaciones:
            raise ValueError(
                f"numero_perforaciones ({self.numero_perforaciones}) no "
                "coincide con la cantidad de coordenadas provistas en "
                f"'perforaciones' ({len(self.perforaciones)})"
            )
        return self
