"""Configuración general de un proyecto.

Cubre dos cosas que no encajan en ninguna de las seis secciones de datos
de entrada:

- ``normativa_referencia``: qué código/norma se usará en las
  verificaciones de resistencia de fases futuras (p. ej. "NSR-10"). Hoy
  es solo una etiqueta de texto: no activa ningún cálculo.
- Las tolerancias que hoy usan las validaciones cruzadas de la Etapa 2
  (``calculo_estructural.validation.configuracion``), para que cada
  proyecto pueda declarar con qué criterio se validó, aunque todavía no
  se puedan ajustar de verdad (ver nota más abajo).

Importante: por ahora estos valores solo se guardan y se cargan junto con
el proyecto — las reglas de ``calculo_estructural.validation`` siguen
usando sus propias constantes fijas (no las de este modelo). Conectarlos
de verdad queda para una fase futura, para no modificar el comportamiento
de las validaciones ya existentes en esta etapa.
"""

from __future__ import annotations

from pydantic import Field

from .base import ProyectoBaseModel


class ConfiguracionProyecto(ProyectoBaseModel):
    """Configuración general de un proyecto."""

    normativa_referencia: str = Field(
        default="",
        description="Código/norma de referencia para verificaciones futuras (p.ej. 'NSR-10')",
    )
    holgura_estandar_perforacion_in: float = Field(
        default=0.125,
        gt=0,
        description=(
            "Sobre-diámetro estándar esperado entre perforación y perno, en in. "
            "Hoy coincide con validation.configuracion.HOLGURA_ESTANDAR_PERFORACION_IN, "
            "que es la que realmente usan las reglas de la Etapa 2."
        ),
    )
    tolerancia_coordenadas_mm: float = Field(
        default=1.0,
        gt=0,
        description=(
            "Distancia por debajo de la cual dos coordenadas se consideran la misma "
            "posición, en mm. Hoy coincide con "
            "validation.configuracion.TOLERANCIA_COORDENADAS_MM."
        ),
    )
