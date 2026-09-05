"""Validaciones cruzadas entre la soldadura y el perfil metálico que conecta.

Que la longitud y el espesor de la soldadura sean valores válidos ya está
garantizado por el propio modelo ``Soldadura`` (Etapa 1, ``Field(gt=0)``);
aquí solo se agrega lo que depende de comparar la soldadura CON el
perfil, que el modelo por sí solo no puede saber.
"""

from __future__ import annotations

from ..calculos.propiedades_geometricas import perimetro_perfil
from ..models import PerfilMetalico, Soldadura
from .resultados import Componente, EstadoValidacion, ResultadoValidacion

_COMPONENTES = [Componente.SOLDADURA, Componente.PERFIL_METALICO]


def validar_longitud_vs_perimetro(soldadura: Soldadura, perfil: PerfilMetalico) -> ResultadoValidacion:
    """Que la longitud de soldadura declarada sea geométricamente
    razonable frente al perímetro exterior del perfil que conecta.

    Si la longitud supera el perímetro no es necesariamente un error (se
    puede soldar por más de un lado, o en más de una pasada) — se marca
    como ADVERTENCIA para que se revise, no como ERROR bloqueante.
    """
    codigo = "SOLDADURA_LONGITUD_VS_PERIMETRO"
    nombre = "Longitud de soldadura vs. perímetro del perfil"
    perimetro = perimetro_perfil(perfil)
    datos = {"longitud_soldadura_mm": soldadura.longitud_mm, "perimetro_perfil_mm": perimetro}

    if soldadura.longitud_mm > perimetro:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ADVERTENCIA,
            mensaje=(
                f"La longitud de soldadura declarada ({soldadura.longitud_mm:.1f} mm) "
                f"supera el perímetro exterior del perfil ({perimetro:.1f} mm). "
                "Puede ser correcto si se suelda por más de un lado o pasada; revisar."
            ),
            componentes=_COMPONENTES,
            datos=datos,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="La longitud de soldadura es compatible con el perímetro del perfil.",
        componentes=_COMPONENTES,
        datos=datos,
    )


def validar_espesor_vs_espesores_conectados() -> ResultadoValidacion:
    """Espesor máximo/mínimo de soldadura de filete según el espesor de
    las piezas conectadas.

    Este es un criterio normativo (p. ej. tablas de AWS D1.1 según
    espesor del material base) que todavía no se ha definido para este
    proyecto. En vez de asumir un valor, se deja marcado explícitamente
    como pendiente.
    """
    return ResultadoValidacion(
        codigo="SOLDADURA_ESPESOR_MAXIMO",
        nombre="Espesor máximo de soldadura vs. piezas conectadas",
        estado=EstadoValidacion.NO_VERIFICADO,
        mensaje=(
            "Pendiente: el espesor máximo/mínimo permitido de una soldadura de "
            "filete según el espesor de las piezas conectadas es un criterio "
            "normativo que todavía no se ha definido en este proyecto."
        ),
        componentes=_COMPONENTES,
    )


def validar(soldadura: Soldadura, perfil: PerfilMetalico) -> list[ResultadoValidacion]:
    """Corre todas las reglas cruzadas entre soldadura y perfil."""
    return [
        validar_longitud_vs_perimetro(soldadura, perfil),
        validar_espesor_vs_espesores_conectados(),
    ]
