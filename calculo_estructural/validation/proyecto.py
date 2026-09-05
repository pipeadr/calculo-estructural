"""Orquesta todas las validaciones cruzadas sobre un Proyecto completo.

Corre cada categoría de reglas solo cuando las secciones que necesita ya
están presentes en el proyecto; cuando falta alguna, devuelve un
resultado NO_VERIFICADO explícito en su lugar (nunca se omite en
silencio), para que la interfaz siempre pueda mostrar el estado de todas
las reglas conocidas, estén o no ya evaluables.
"""

from __future__ import annotations

from ..models import Proyecto
from . import cargas as _cargas
from . import geometria_placa as _geometria_placa
from . import pernos_concreto as _pernos_concreto
from . import pernos_perforaciones as _pernos_perforaciones
from . import soldadura_perfil as _soldadura_perfil
from .resultados import Componente, EstadoValidacion, ResultadoValidacion


def _no_verificado(
    codigo: str, nombre: str, mensaje: str, componentes: list[Componente]
) -> ResultadoValidacion:
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.NO_VERIFICADO,
        mensaje=mensaje,
        componentes=componentes,
    )


def validar_proyecto(proyecto: Proyecto) -> list[ResultadoValidacion]:
    """Corre todas las reglas de validación cruzada aplicables según qué
    secciones del proyecto ya están completas."""
    resultados: list[ResultadoValidacion] = []

    if proyecto.pernos is not None and proyecto.placa_base is not None:
        resultados.extend(_pernos_perforaciones.validar(proyecto.pernos, proyecto.placa_base))
    else:
        resultados.append(
            _no_verificado(
                "PERNO_PERFORACION",
                "Pernos y perforaciones",
                "Falta placa_base y/o pernos para validar esta relación.",
                [Componente.PERNOS, Componente.PLACA_BASE],
            )
        )

    if proyecto.placa_base is not None:
        resultados.extend(
            _geometria_placa.validar(proyecto.placa_base, proyecto.perfil_metalico, proyecto.pernos)
        )
    else:
        resultados.append(
            _no_verificado(
                "GEOMETRIA_PLACA",
                "Geometría de la placa",
                "Falta placa_base para validar su geometría.",
                [Componente.PLACA_BASE],
            )
        )

    if proyecto.pernos is not None and proyecto.elemento_concreto is not None:
        resultados.extend(_pernos_concreto.validar(proyecto.pernos, proyecto.elemento_concreto))
    else:
        resultados.append(
            _no_verificado(
                "PERNO_CONCRETO",
                "Pernos y concreto",
                "Falta pernos y/o elemento_concreto para validar esta relación.",
                [Componente.PERNOS, Componente.ELEMENTO_CONCRETO],
            )
        )

    if proyecto.soldadura is not None and proyecto.perfil_metalico is not None:
        resultados.extend(_soldadura_perfil.validar(proyecto.soldadura, proyecto.perfil_metalico))
    else:
        resultados.append(
            _no_verificado(
                "SOLDADURA_PERFIL",
                "Soldadura y perfil",
                "Falta soldadura y/o perfil_metalico para validar esta relación.",
                [Componente.SOLDADURA, Componente.PERFIL_METALICO],
            )
        )

    if proyecto.cargas is not None:
        resultados.extend(_cargas.validar(proyecto.cargas))
    else:
        resultados.append(
            _no_verificado(
                "CARGAS",
                "Cargas",
                "Falta definir las cargas para validarlas.",
                [Componente.CARGAS],
            )
        )

    return resultados


def hay_errores(resultados: list[ResultadoValidacion]) -> bool:
    """True si algún resultado tiene estado ERROR (bloqueante)."""
    return any(r.estado == EstadoValidacion.ERROR for r in resultados)


def resumen_por_estado(resultados: list[ResultadoValidacion]) -> dict[str, int]:
    """Cuenta cuántos resultados hay por cada estado — útil para la UI,
    p.ej. un resumen "3 errores, 2 advertencias, 5 OK"."""
    conteo = {estado.value: 0 for estado in EstadoValidacion}
    for resultado in resultados:
        conteo[resultado.estado.value] += 1
    return conteo
