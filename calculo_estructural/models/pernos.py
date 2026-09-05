"""Modelo de datos de los pernos de anclaje."""

from __future__ import annotations

from pydantic import Field, model_validator

from .base import MM_POR_PULGADA, ProyectoBaseModel, PuntoCoordenado, requerir_si
from .enums import TipoGradoPerno


class PosicionPerno(PuntoCoordenado):
    """Posición (x, y) en mm de un perno, respecto al centroide de la
    placa base (mismo sistema de referencia que las perforaciones)."""


class Pernos(ProyectoBaseModel):
    """Grupo de pernos de anclaje.

    En esta fase todos los pernos del grupo comparten diámetro, longitud,
    grado y profundidad de embebido; solo la posición varía perno a perno.
    """

    cantidad: int = Field(gt=0, description="Cantidad de pernos")
    diametro_in: float = Field(gt=0, description="Diámetro del perno en pulgadas")
    longitud_mm: float = Field(gt=0, description="Longitud total del perno en mm")
    tipo_grado: TipoGradoPerno
    tipo_grado_otro: str | None = Field(
        default=None, description="Obligatorio si tipo_grado == OTRO"
    )
    profundidad_embebido_mm: float = Field(
        gt=0, description="Profundidad de embebido en el concreto, en mm"
    )
    posiciones: list[PosicionPerno] = Field(
        default_factory=list,
        description="Coordenadas (x, y) en mm de cada perno",
    )

    @property
    def diametro_mm(self) -> float:
        """Diámetro del perno convertido a milímetros (recalculado a
        partir de ``diametro_in``; no se serializa, ver nota en
        ``PlacaBase.diametro_perforacion_mm``)."""
        return self.diametro_in * MM_POR_PULGADA

    @model_validator(mode="after")
    def _validar_consistencia(self) -> "Pernos":
        requerir_si(
            self.tipo_grado == TipoGradoPerno.OTRO,
            self.tipo_grado_otro,
            "tipo_grado_otro es obligatorio cuando tipo_grado es OTRO",
        )
        if len(self.posiciones) != self.cantidad:
            raise ValueError(
                f"cantidad ({self.cantidad}) no coincide con la cantidad de "
                f"coordenadas provistas en 'posiciones' ({len(self.posiciones)})"
            )
        return self
