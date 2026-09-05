"""Modelo de datos del perfil metálico.

El perfil se modela como una unión discriminada por ``tipo_seccion``: cada
forma (rectangular, cuadrada, circular, I, H) es una clase distinta que
solo admite los campos geométricos que le corresponden — por ejemplo, una
sección circular no acepta ``espesor_alma_mm``.

Para las secciones rectangular, cuadrada y circular se incluye además
``es_hueco`` / ``espesor_pared_mm`` porque en conexiones placa-perfil es
muy común que la columna sea un perfil tubular (HSS). Es un dato
geométrico preparatorio para fases futuras, no una fórmula de resistencia.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import Field, model_validator

from .base import ProyectoBaseModel, requerir_si
from .enums import TipoAcero, TipoSeccionPerfil


def _validar_espesor_pared(es_hueco: bool, espesor_pared_mm: float | None) -> None:
    """Regla compartida por los perfiles rectangular/cuadrado/circular: si
    el perfil es tubular (``es_hueco``), el espesor de pared es
    obligatorio."""
    requerir_si(
        es_hueco,
        espesor_pared_mm,
        "espesor_pared_mm es obligatorio cuando es_hueco es True",
    )


class _PerfilBase(ProyectoBaseModel):
    """Campos comunes a cualquier forma de perfil metálico."""

    tipo_acero: TipoAcero
    tipo_acero_otro: str | None = Field(
        default=None, description="Obligatorio si tipo_acero == OTRO"
    )
    fy_mpa: float = Field(gt=0, description="Esfuerzo de fluencia Fy en MPa")

    @model_validator(mode="after")
    def _validar_tipo_acero_otro(self) -> "_PerfilBase":
        requerir_si(
            self.tipo_acero == TipoAcero.OTRO,
            self.tipo_acero_otro,
            "tipo_acero_otro es obligatorio cuando tipo_acero es OTRO",
        )
        return self


class PerfilRectangular(_PerfilBase):
    """Perfil de sección rectangular, maciza o tubular (HSS rectangular)."""

    tipo_seccion: Literal[TipoSeccionPerfil.RECTANGULAR] = (
        TipoSeccionPerfil.RECTANGULAR
    )
    b_mm: float = Field(gt=0, description="Ancho de la sección en mm")
    h_mm: float = Field(gt=0, description="Altura de la sección en mm")
    es_hueco: bool = False
    espesor_pared_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _validar_hueco(self) -> "PerfilRectangular":
        _validar_espesor_pared(self.es_hueco, self.espesor_pared_mm)
        return self


class PerfilCuadrado(_PerfilBase):
    """Perfil de sección cuadrada, maciza o tubular (HSS cuadrado)."""

    tipo_seccion: Literal[TipoSeccionPerfil.CUADRADA] = (
        TipoSeccionPerfil.CUADRADA
    )
    lado_mm: float = Field(gt=0, description="Lado de la sección en mm")
    es_hueco: bool = False
    espesor_pared_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _validar_hueco(self) -> "PerfilCuadrado":
        _validar_espesor_pared(self.es_hueco, self.espesor_pared_mm)
        return self


class PerfilCircular(_PerfilBase):
    """Perfil de sección circular, maciza o tubular (HSS circular / tubo)."""

    tipo_seccion: Literal[TipoSeccionPerfil.CIRCULAR] = (
        TipoSeccionPerfil.CIRCULAR
    )
    diametro_mm: float = Field(gt=0, description="Diámetro de la sección en mm")
    es_hueco: bool = False
    espesor_pared_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _validar_hueco(self) -> "PerfilCircular":
        _validar_espesor_pared(self.es_hueco, self.espesor_pared_mm)
        return self


class _PerfilIHBase(_PerfilBase):
    """Campos comunes a los perfiles de ala ancha (I y H): los mismos 4
    parámetros geométricos estándar."""

    peralte_mm: float = Field(gt=0, description="Peralte total (d) en mm")
    ancho_ala_mm: float = Field(gt=0, description="Ancho del ala (bf) en mm")
    espesor_ala_mm: float = Field(gt=0, description="Espesor del ala (tf) en mm")
    espesor_alma_mm: float = Field(gt=0, description="Espesor del alma (tw) en mm")


class PerfilI(_PerfilIHBase):
    """Perfil de sección I."""

    tipo_seccion: Literal[TipoSeccionPerfil.I] = TipoSeccionPerfil.I


class PerfilH(_PerfilIHBase):
    """Perfil de sección H (ala ancha)."""

    tipo_seccion: Literal[TipoSeccionPerfil.H] = TipoSeccionPerfil.H


PerfilMetalico = Annotated[
    Union[PerfilRectangular, PerfilCuadrado, PerfilCircular, PerfilI, PerfilH],
    Field(discriminator="tipo_seccion"),
]
