"""Formularios de sección, uno por cada parte editable del proyecto.

Todos heredan de ``SeccionFormBase``: reconstruyen su propio sub-modelo
de Pydantic a partir de sus widgets y dejan que Pydantic valide — nunca
reimplementan una regla de ``models`` o ``validation``.
"""

from __future__ import annotations

from .base_form import CamposMaterial, SeccionFormBase, señales_bloqueadas
from .cargas_form import CargasForm
from .datos_generales_form import DatosGeneralesForm
from .elemento_concreto_form import ElementoConcretoForm
from .perfil_metalico_form import PerfilMetalicoForm
from .placa_base_form import PlacaBaseForm
from .pernos_form import PernosForm
from .soldadura_form import SoldaduraForm

__all__ = [
    "SeccionFormBase",
    "CamposMaterial",
    "señales_bloqueadas",
    "DatosGeneralesForm",
    "PlacaBaseForm",
    "PerfilMetalicoForm",
    "ElementoConcretoForm",
    "PernosForm",
    "SoldaduraForm",
    "CargasForm",
]
