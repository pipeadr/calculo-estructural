"""Validaciones cruzadas entre los pernos de anclaje y el elemento de
concreto que los recibe.

Nota de diseño: el modelo de datos actual no define una excentricidad
entre la placa base y el elemento de concreto, así que aquí también se
asume que comparten el mismo eje/centroide en planta (igual que se asume
para el perfil en ``geometria_placa``). Cuando se agregue esa
excentricidad en una fase futura, esta regla deberá recibir el
desplazamiento correspondiente.

No se implementan aquí verificaciones de resistencia del concreto
(breakout, pullout, etc.) — son geometría/compatibilidad dimensional.
"""

from __future__ import annotations

from ..models import ElementoConcreto, Pernos
from .resultados import Componente, EstadoValidacion, ResultadoValidacion

_COMPONENTES = [Componente.PERNOS, Componente.ELEMENTO_CONCRETO]


def validar_pernos_dentro_del_concreto(pernos: Pernos, concreto: ElementoConcreto) -> ResultadoValidacion:
    """Que cada perno, en planta, quede dentro del área del elemento de
    concreto (distancias a sus bordes positivas)."""
    codigo = "PERNOS_DENTRO_DEL_CONCRETO"
    nombre = "Pernos dentro del elemento de concreto"
    medio_largo = concreto.largo_mm / 2
    medio_ancho = concreto.ancho_mm / 2

    fuera = [
        {
            "indice": indice,
            "x_mm": perno.x_mm,
            "y_mm": perno.y_mm,
            "distancia_borde_x_mm": medio_largo - abs(perno.x_mm),
            "distancia_borde_y_mm": medio_ancho - abs(perno.y_mm),
        }
        for indice, perno in enumerate(pernos.posiciones)
        if abs(perno.x_mm) > medio_largo or abs(perno.y_mm) > medio_ancho
    ]

    if fuera:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"{len(fuera)} perno(s) quedan fuera del área en planta del elemento "
                "de concreto (asumiendo el mismo eje que la placa)."
            ),
            componentes=_COMPONENTES,
            datos={"pernos_fuera": fuera},
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="Todos los pernos están dentro del área en planta del elemento de concreto.",
        componentes=_COMPONENTES,
    )


def validar_embebido_dentro_de_altura(pernos: Pernos, concreto: ElementoConcreto) -> ResultadoValidacion:
    """Que la profundidad de embebido quepa dentro de la altura/espesor
    del elemento de concreto (el perno no debería atravesarlo)."""
    codigo = "EMBEBIDO_DENTRO_DE_ALTURA"
    nombre = "Profundidad de embebido vs. altura del concreto"
    datos = {
        "profundidad_embebido_mm": pernos.profundidad_embebido_mm,
        "altura_concreto_mm": concreto.altura_mm,
    }

    if pernos.profundidad_embebido_mm > concreto.altura_mm:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"La profundidad de embebido ({pernos.profundidad_embebido_mm:.1f} mm) "
                f"supera la altura del elemento de concreto ({concreto.altura_mm:.1f} mm): "
                "el perno atravesaría el elemento."
            ),
            componentes=_COMPONENTES,
            datos=datos,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="La profundidad de embebido cabe dentro de la altura del elemento de concreto.",
        componentes=_COMPONENTES,
        datos=datos,
    )


def validar(pernos: Pernos, concreto: ElementoConcreto) -> list[ResultadoValidacion]:
    """Corre todas las reglas cruzadas entre pernos y elemento de concreto."""
    return [
        validar_pernos_dentro_del_concreto(pernos, concreto),
        validar_embebido_dentro_de_altura(pernos, concreto),
    ]
