"""Validaciones cruzadas de geometría en planta de la placa base: que las
perforaciones y el perfil queden dentro de su contorno, que las
perforaciones no se superpongan, y que los pernos también queden dentro.

Nota de diseño: el modelo de datos actual no define una excentricidad del
perfil metálico respecto a la placa, así que se asume que el perfil está
centrado en el mismo origen que las perforaciones (el centroide de la
placa). Cuando se agregue esa excentricidad en una fase futura, la regla
``validar_perfil_dentro_de_placa`` deberá recibir el desplazamiento.
"""

from __future__ import annotations

from ..calculos.propiedades_geometricas import bounding_box_perfil, distancia_entre_puntos
from ..models import PerfilMetalico, PlacaBase, Pernos
from .resultados import Componente, EstadoValidacion, ResultadoValidacion


def validar_perforaciones_dentro_de_placa(placa: PlacaBase) -> ResultadoValidacion:
    """Que cada perforación (con su radio) quede dentro del contorno de
    la placa, es decir que su distancia a cada borde sea positiva."""
    codigo = "PERFORACIONES_DENTRO_DE_PLACA"
    nombre = "Perforaciones dentro de la placa"
    radio = placa.diametro_perforacion_mm / 2
    medio_largo = placa.largo_mm / 2
    medio_ancho = placa.ancho_mm / 2

    fuera = []
    for indice, perforacion in enumerate(placa.perforaciones):
        distancia_borde_x = medio_largo - abs(perforacion.x_mm) - radio
        distancia_borde_y = medio_ancho - abs(perforacion.y_mm) - radio
        if distancia_borde_x < 0 or distancia_borde_y < 0:
            fuera.append(
                {
                    "indice": indice,
                    "x_mm": perforacion.x_mm,
                    "y_mm": perforacion.y_mm,
                    "distancia_borde_x_mm": distancia_borde_x,
                    "distancia_borde_y_mm": distancia_borde_y,
                }
            )

    if fuera:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"{len(fuera)} perforación(es) quedan fuera de la placa o "
                "demasiado cerca del borde (distancia de borde negativa)."
            ),
            componentes=[Componente.PLACA_BASE],
            datos={"perforaciones_fuera": fuera},
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="Todas las perforaciones están dentro de la placa, con distancia de borde positiva.",
        componentes=[Componente.PLACA_BASE],
    )


def validar_perforaciones_sin_superposicion(placa: PlacaBase) -> ResultadoValidacion:
    """Que ninguna pareja de perforaciones se superponga (distancia entre
    centros menor que el diámetro de perforación)."""
    codigo = "PERFORACIONES_SUPERPUESTAS"
    nombre = "Perforaciones sin superposición"
    diametro = placa.diametro_perforacion_mm
    posiciones = [(p.x_mm, p.y_mm) for p in placa.perforaciones]

    superpuestas = [
        {"indice_a": i, "indice_b": j, "distancia_mm": distancia_entre_puntos(posiciones[i], posiciones[j])}
        for i in range(len(posiciones))
        for j in range(i + 1, len(posiciones))
        if distancia_entre_puntos(posiciones[i], posiciones[j]) < diametro
    ]

    if superpuestas:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=f"{len(superpuestas)} par(es) de perforaciones se superponen entre sí.",
            componentes=[Componente.PLACA_BASE],
            datos={"pares_superpuestos": superpuestas},
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="No hay perforaciones superpuestas.",
        componentes=[Componente.PLACA_BASE],
    )


def validar_perfil_dentro_de_placa(perfil: PerfilMetalico, placa: PlacaBase) -> ResultadoValidacion:
    """Que el rectángulo envolvente del perfil (asumido centrado en la
    placa) quepa dentro del contorno de la placa."""
    codigo = "PERFIL_DENTRO_DE_PLACA"
    nombre = "Perfil dentro de la placa"
    ancho_perfil_x, ancho_perfil_y = bounding_box_perfil(perfil)
    datos = {
        "ancho_perfil_x_mm": ancho_perfil_x,
        "ancho_perfil_y_mm": ancho_perfil_y,
        "largo_placa_mm": placa.largo_mm,
        "ancho_placa_mm": placa.ancho_mm,
    }

    if ancho_perfil_x > placa.largo_mm or ancho_perfil_y > placa.ancho_mm:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"El perfil ({ancho_perfil_x:.1f}x{ancho_perfil_y:.1f} mm, asumido "
                f"centrado en la placa) no cabe dentro de la placa "
                f"({placa.largo_mm:.1f}x{placa.ancho_mm:.1f} mm)."
            ),
            componentes=[Componente.PERFIL_METALICO, Componente.PLACA_BASE],
            datos=datos,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="El perfil cabe dentro del contorno de la placa.",
        componentes=[Componente.PERFIL_METALICO, Componente.PLACA_BASE],
        datos=datos,
    )


def validar_pernos_dentro_de_placa(pernos: Pernos, placa: PlacaBase) -> ResultadoValidacion:
    """Que cada perno quede dentro del contorno rectangular de la placa."""
    codigo = "PERNOS_DENTRO_DE_PLACA"
    nombre = "Pernos dentro de la placa"
    medio_largo = placa.largo_mm / 2
    medio_ancho = placa.ancho_mm / 2

    fuera = [
        {"indice": indice, "x_mm": perno.x_mm, "y_mm": perno.y_mm}
        for indice, perno in enumerate(pernos.posiciones)
        if abs(perno.x_mm) > medio_largo or abs(perno.y_mm) > medio_ancho
    ]

    if fuera:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=f"{len(fuera)} perno(s) quedan fuera del contorno de la placa.",
            componentes=[Componente.PERNOS, Componente.PLACA_BASE],
            datos={"pernos_fuera": fuera},
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="Todos los pernos están dentro del contorno de la placa.",
        componentes=[Componente.PERNOS, Componente.PLACA_BASE],
    )


def validar(
    placa: PlacaBase,
    perfil: PerfilMetalico | None,
    pernos: Pernos | None,
) -> list[ResultadoValidacion]:
    """Corre las reglas geométricas de la placa. ``perfil``/``pernos`` son
    opcionales: si faltan, se reporta NO_VERIFICADO en su lugar."""
    resultados = [
        validar_perforaciones_dentro_de_placa(placa),
        validar_perforaciones_sin_superposicion(placa),
    ]

    if perfil is not None:
        resultados.append(validar_perfil_dentro_de_placa(perfil, placa))
    else:
        resultados.append(
            ResultadoValidacion(
                codigo="PERFIL_DENTRO_DE_PLACA",
                nombre="Perfil dentro de la placa",
                estado=EstadoValidacion.NO_VERIFICADO,
                mensaje="No se puede verificar: falta definir el perfil metálico.",
                componentes=[Componente.PERFIL_METALICO, Componente.PLACA_BASE],
            )
        )

    if pernos is not None:
        resultados.append(validar_pernos_dentro_de_placa(pernos, placa))
    else:
        resultados.append(
            ResultadoValidacion(
                codigo="PERNOS_DENTRO_DE_PLACA",
                nombre="Pernos dentro de la placa",
                estado=EstadoValidacion.NO_VERIFICADO,
                mensaje="No se puede verificar: falta definir los pernos.",
                componentes=[Componente.PERNOS, Componente.PLACA_BASE],
            )
        )

    return resultados
