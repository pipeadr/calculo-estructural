"""Validaciones cruzadas entre los pernos de anclaje y las perforaciones
de la placa base: cantidad, correspondencia de posiciones, compatibilidad
de diámetro, y ausencia de duplicados."""

from __future__ import annotations

from ..calculos.propiedades_geometricas import distancia_entre_puntos
from ..models import PlacaBase, Pernos
from .configuracion import (
    HOLGURA_ESTANDAR_PERFORACION_IN,
    TOLERANCIA_COORDENADAS_MM,
    TOLERANCIA_DIAMETRO_IN,
)
from .resultados import Componente, EstadoValidacion, ResultadoValidacion

_COMPONENTES = [Componente.PERNOS, Componente.PLACA_BASE]


def validar_cantidad(pernos: Pernos, placa: PlacaBase) -> ResultadoValidacion:
    """Que la cantidad de pernos sea coherente con el número de
    perforaciones disponibles en la placa."""
    codigo = "PERNO_PERFORACION_CANTIDAD"
    nombre = "Cantidad de pernos vs. perforaciones"
    datos = {
        "cantidad_pernos": pernos.cantidad,
        "numero_perforaciones": placa.numero_perforaciones,
    }

    if pernos.cantidad > placa.numero_perforaciones:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"Hay {pernos.cantidad} pernos declarados pero solo "
                f"{placa.numero_perforaciones} perforaciones en la placa: "
                "no todos los pernos tienen dónde ir."
            ),
            componentes=_COMPONENTES,
            datos=datos,
        )
    if pernos.cantidad < placa.numero_perforaciones:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ADVERTENCIA,
            mensaje=(
                f"Hay {placa.numero_perforaciones} perforaciones pero solo "
                f"{pernos.cantidad} pernos: quedarían "
                f"{placa.numero_perforaciones - pernos.cantidad} perforación(es) sin perno."
            ),
            componentes=_COMPONENTES,
            datos=datos,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="La cantidad de pernos coincide con el número de perforaciones.",
        componentes=_COMPONENTES,
        datos=datos,
    )


def validar_correspondencia_posiciones(pernos: Pernos, placa: PlacaBase) -> ResultadoValidacion:
    """Que cada perno tenga una perforación en su misma posición (dentro
    de una tolerancia de entrada manual de datos)."""
    codigo = "PERNO_PERFORACION_CORRESPONDENCIA"
    nombre = "Correspondencia de coordenadas perno-perforación"

    sin_correspondencia = []
    for indice, perno in enumerate(pernos.posiciones):
        tiene_perforacion = any(
            distancia_entre_puntos((perno.x_mm, perno.y_mm), (perf.x_mm, perf.y_mm))
            <= TOLERANCIA_COORDENADAS_MM
            for perf in placa.perforaciones
        )
        if not tiene_perforacion:
            sin_correspondencia.append({"indice": indice, "x_mm": perno.x_mm, "y_mm": perno.y_mm})

    if sin_correspondencia:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"{len(sin_correspondencia)} perno(s) no tienen una perforación en su "
                f"misma posición (tolerancia {TOLERANCIA_COORDENADAS_MM} mm)."
            ),
            componentes=_COMPONENTES,
            datos={"pernos_sin_perforacion": sin_correspondencia},
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje="Todos los pernos tienen una perforación correspondiente.",
        componentes=_COMPONENTES,
    )


def validar_diametro_compatible(pernos: Pernos, placa: PlacaBase) -> ResultadoValidacion:
    """Que el diámetro de la perforación sea compatible con el del perno:
    debe ser 1/8" mayor (dato indicado explícitamente para este
    proyecto). Si la perforación es más chica que el perno -> ERROR (no
    cabe físicamente); si la holgura real difiere de 1/8" -> ADVERTENCIA
    (cabe, pero no con la holgura estándar)."""
    codigo = "PERNO_PERFORACION_DIAMETRO"
    nombre = "Compatibilidad de diámetro perno-perforación"

    holgura_real = placa.diametro_perforacion_in - pernos.diametro_in
    datos = {
        "diametro_perno_in": pernos.diametro_in,
        "diametro_perforacion_in": placa.diametro_perforacion_in,
        "holgura_estandar_in": HOLGURA_ESTANDAR_PERFORACION_IN,
        "holgura_real_in": holgura_real,
    }

    if holgura_real < 0:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=(
                f"El perno (diámetro {pernos.diametro_in} in) no cabe en la "
                f"perforación (diámetro {placa.diametro_perforacion_in} in): "
                "la perforación es más pequeña que el perno."
            ),
            componentes=_COMPONENTES,
            datos=datos,
        )
    if abs(holgura_real - HOLGURA_ESTANDAR_PERFORACION_IN) <= TOLERANCIA_DIAMETRO_IN:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.OK,
            mensaje=(
                f"La perforación (diámetro {placa.diametro_perforacion_in} in) es 1/8 in "
                f"mayor que el perno (diámetro {pernos.diametro_in} in), como corresponde."
            ),
            componentes=_COMPONENTES,
            datos=datos,
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.ADVERTENCIA,
        mensaje=(
            f"La holgura entre perforación ({placa.diametro_perforacion_in} in) y perno "
            f"({pernos.diametro_in} in) es {holgura_real:.4g} in, distinta de la holgura "
            f"estándar de {HOLGURA_ESTANDAR_PERFORACION_IN} in."
        ),
        componentes=_COMPONENTES,
        datos=datos,
    )


def _validar_posiciones_sin_duplicados(
    *,
    codigo: str,
    nombre: str,
    posiciones: list[tuple[float, float]],
    componente: Componente,
    mensaje_error: str,
    mensaje_ok: str,
) -> ResultadoValidacion:
    duplicados = [
        {"indice_a": i, "indice_b": j}
        for i in range(len(posiciones))
        for j in range(i + 1, len(posiciones))
        if distancia_entre_puntos(posiciones[i], posiciones[j]) <= TOLERANCIA_COORDENADAS_MM
    ]

    if duplicados:
        return ResultadoValidacion(
            codigo=codigo,
            nombre=nombre,
            estado=EstadoValidacion.ERROR,
            mensaje=f"{mensaje_error}: {len(duplicados)} par(es) repetidos.",
            componentes=[componente],
            datos={"pares_duplicados": duplicados},
        )
    return ResultadoValidacion(
        codigo=codigo,
        nombre=nombre,
        estado=EstadoValidacion.OK,
        mensaje=mensaje_ok,
        componentes=[componente],
    )


def validar_sin_duplicados(pernos: Pernos, placa: PlacaBase) -> list[ResultadoValidacion]:
    """Que no existan pernos duplicados ni perforaciones duplicadas
    (misma posición dentro de la tolerancia de coordenadas)."""
    return [
        _validar_posiciones_sin_duplicados(
            codigo="PERNOS_DUPLICADOS",
            nombre="Pernos duplicados",
            posiciones=[(p.x_mm, p.y_mm) for p in pernos.posiciones],
            componente=Componente.PERNOS,
            mensaje_error="Hay pernos en la misma posición",
            mensaje_ok="No hay pernos duplicados.",
        ),
        _validar_posiciones_sin_duplicados(
            codigo="PERFORACIONES_DUPLICADAS",
            nombre="Perforaciones duplicadas",
            posiciones=[(p.x_mm, p.y_mm) for p in placa.perforaciones],
            componente=Componente.PLACA_BASE,
            mensaje_error="Hay perforaciones en la misma posición",
            mensaje_ok="No hay perforaciones duplicadas.",
        ),
    ]


def validar(pernos: Pernos, placa: PlacaBase) -> list[ResultadoValidacion]:
    """Corre todas las reglas cruzadas entre pernos y perforaciones."""
    resultados = [
        validar_cantidad(pernos, placa),
        validar_correspondencia_posiciones(pernos, placa),
        validar_diametro_compatible(pernos, placa),
    ]
    resultados.extend(validar_sin_duplicados(pernos, placa))
    return resultados
