"""Modelo de datos de las cargas y momentos aplicados al perfil metálico,
en la interfaz con la placa base.

Fase 1 no define una convención de signos normativa propia (eso depende
de las verificaciones de resistencia que se agregarán en fases futuras):
en su lugar, ``convencion_signos`` deja que quien carga el proyecto
documente en texto libre la convención que está usando, y la Etapa 2
valida que no se haya dejado sin definir. Igualmente, ``tipo_combinacion``
no impone LRFD ni ASD: solo registra cuál se está usando, para que la
validación cruzada pueda advertir si no se indicó.
"""

from __future__ import annotations

from pydantic import Field

from .base import ProyectoBaseModel
from .enums import TipoCombinacionCarga


class Cargas(ProyectoBaseModel):
    """Cargas y momentos en kN / kN·m."""

    axial_kn: float = Field(description="Carga axial en kN")
    cortante_x_kn: float = Field(description="Cortante en dirección X en kN")
    cortante_y_kn: float = Field(description="Cortante en dirección Y en kN")
    momento_x_knm: float = Field(description="Momento respecto al eje X en kN·m")
    momento_y_knm: float = Field(description="Momento respecto al eje Y en kN·m")
    momento_z_knm: float = Field(description="Momento respecto al eje Z en kN·m")

    tipo_combinacion: TipoCombinacionCarga = Field(
        default=TipoCombinacionCarga.NO_ESPECIFICADA,
        description="Si las cargas son factorizadas (LRFD) o admisibles/de servicio (ASD)",
    )
    convencion_signos: str = Field(
        default="",
        description="Descripción en texto libre de la convención de signos usada, p.ej. 'axial positivo = compresión'",
    )
