"""Validaciones relacionadas con las cargas.

Que las cargas tengan valores numéricos, y que fuerzas/momentos estén en
kN y kN·m respectivamente, ya está garantizado por el propio modelo
``Cargas``: los nombres de campo fijan la unidad (sufijos ``_kn`` /
``_knm``) y Pydantic exige tipo ``float`` en la construcción — no puede
existir una instancia de ``Cargas`` con una unidad "incorrecta" o un
valor no numérico. Por eso esa regla siempre da OK aquí: se reporta
igual, de forma explícita, para que quede constancia en el reporte de
validación en vez de omitirse en silencio.

Lo que sí depende de una decisión de quien carga el proyecto — y por lo
tanto sí hace falta validar en tiempo de ejecución — es si se documentó
una convención de signos y si se indicó el tipo de combinación de carga.
"""

from __future__ import annotations

from ..models import Cargas, TipoCombinacionCarga
from .resultados import Componente, EstadoValidacion, ResultadoValidacion

_COMPONENTES = [Componente.CARGAS]


def validar_unidades_y_valores_numericos(cargas: Cargas) -> ResultadoValidacion:
    """Unidades coherentes (kN / kN·m) y valores numéricos: garantizado
    por el modelo de datos, se reporta como constancia explícita."""
    return ResultadoValidacion(
        codigo="CARGAS_UNIDADES_Y_VALORES",
        nombre="Unidades y valores numéricos de las cargas",
        estado=EstadoValidacion.OK,
        mensaje=(
            "Garantizado por el modelo de datos: los campos de Cargas son "
            "siempre numéricos y están fijos en kN (fuerzas) y kN·m (momentos)."
        ),
        componentes=_COMPONENTES,
    )


def validar_convencion_signos(cargas: Cargas) -> ResultadoValidacion:
    """Que exista una convención de signos documentada para las cargas."""
    codigo = "CARGAS_CONVENCION_SIGNOS"
    nombre = "Convención de signos definida"

    if not cargas.convencion_signos.strip():
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ADVERTENCIA,
            mensaje=(
                "No se documentó una convención de signos para las cargas "
                "(campo 'convencion_signos' vacío). Será necesaria antes de "
                "interpretar resultados de verificaciones futuras."
            ),
            componentes=_COMPONENTES,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje=f'Convención de signos documentada: "{cargas.convencion_signos}".',
        componentes=_COMPONENTES,
    )


def validar_tipo_combinacion(cargas: Cargas) -> ResultadoValidacion:
    """Que se haya indicado si las cargas son factorizadas o admisibles,
    para no mezclarlas sin darse cuenta entre distintos casos de carga."""
    codigo = "CARGAS_TIPO_COMBINACION"
    nombre = "Tipo de combinación de carga indicado"

    if cargas.tipo_combinacion == TipoCombinacionCarga.NO_ESPECIFICADA:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ADVERTENCIA,
            mensaje=(
                "No se indicó si estas cargas son factorizadas (LRFD) o "
                "admisibles/de servicio (ASD). Sin esto no se puede garantizar "
                "que no se mezclen ambos tipos entre distintos casos de carga."
            ),
            componentes=_COMPONENTES,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje=f"Las cargas están indicadas como '{cargas.tipo_combinacion.value}'.",
        componentes=_COMPONENTES,
    )


def validar(cargas: Cargas) -> list[ResultadoValidacion]:
    """Corre todas las reglas relacionadas con las cargas."""
    return [
        validar_unidades_y_valores_numericos(cargas),
        validar_convencion_signos(cargas),
        validar_tipo_combinacion(cargas),
    ]
