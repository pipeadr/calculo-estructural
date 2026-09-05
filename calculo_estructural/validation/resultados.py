"""Estructura común del resultado de una validación cruzada.

Cada regla de ``calculo_estructural.validation`` devuelve uno o más
``ResultadoValidacion`` — nunca imprime nada por su cuenta — para que la
interfaz gráfica (Etapa 6) pueda consumirlos directamente: mostrarlos en
una lista, resaltar el componente involucrado, o usar ``datos`` para
señalar exactamente qué corregir.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from ..models.base import ProyectoBaseModel


class EstadoValidacion(str, Enum):
    """Resultado de evaluar una regla de validación."""

    OK = "OK"
    ERROR = "ERROR"
    ADVERTENCIA = "ADVERTENCIA"
    NO_VERIFICADO = "NO_VERIFICADO"


class Componente(str, Enum):
    """Componentes del proyecto que una regla de validación puede
    involucrar (una regla cruzada normalmente lista dos o más)."""

    PROYECTO = "proyecto"
    PLACA_BASE = "placa_base"
    PERFIL_METALICO = "perfil_metalico"
    ELEMENTO_CONCRETO = "elemento_concreto"
    PERNOS = "pernos"
    SOLDADURA = "soldadura"
    CARGAS = "cargas"


class ResultadoValidacion(ProyectoBaseModel):
    """Resultado de una regla de validación individual.

    ``datos`` lleva la información estructurada que la interfaz necesita
    para señalar o ayudar a corregir el problema (p. ej. el índice y las
    coordenadas del perno involucrado), sin tener que volver a parsear
    ``mensaje`` como texto libre.
    """

    codigo: str = Field(
        description="Identificador estable de la regla, p.ej. 'PERNO_PERFORACION_DIAMETRO'"
    )
    nombre: str = Field(description="Nombre corto y legible de la regla")
    estado: EstadoValidacion
    mensaje: str
    componentes: list[Componente] = Field(default_factory=list)
    datos: dict[str, Any] = Field(default_factory=dict)

    @property
    def es_bloqueante(self) -> bool:
        """True si este resultado por sí solo impide considerar válido
        el proyecto (severidad ERROR)."""
        return self.estado == EstadoValidacion.ERROR
