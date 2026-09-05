"""Clases y utilidades base compartidas por todos los modelos de datos.

Todas las entidades del dominio (placa base, perfil metálico, elemento de
concreto, pernos, soldadura, cargas, proyecto) heredan de
:class:`ProyectoBaseModel` para compartir la misma configuración de
validación de Pydantic.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

MM_POR_PULGADA = 25.4
"""Factor de conversión de pulgadas a milímetros (1 in = 25.4 mm, exacto)."""


class ProyectoBaseModel(BaseModel):
    """Configuración común para todos los modelos del dominio.

    - ``validate_assignment``: revalida el modelo cada vez que se reasigna
      un atributo (p. ej. ``placa.largo_mm = -5`` dispara la validación al
      vuelo), no solo en la construcción inicial.
    - ``extra="forbid"``: rechaza campos desconocidos, para detectar
      errores de tipeo o archivos de proyecto de versiones incompatibles.
    - ``str_strip_whitespace``: recorta espacios en blanco accidentales en
      campos de texto.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class PuntoCoordenado(ProyectoBaseModel):
    """Posición (x, y) en milímetros.

    Por convención, el origen es el centroide (centro geométrico) de la
    placa base, con X a lo largo de ``largo_mm`` y Y a lo largo de
    ``ancho_mm``. La usan tanto las perforaciones de la placa como las
    posiciones de los pernos, para que ambas listas compartan el mismo
    sistema de referencia.
    """

    x_mm: float
    y_mm: float


def requerir_si(condicion: bool, valor: object, mensaje: str) -> None:
    """Lanza ``ValueError(mensaje)`` si ``condicion`` es verdadera y
    ``valor`` está vacío (``None`` o cadena en blanco).

    Utilidad compartida para el patrón "campo de texto libre obligatorio
    solo cuando se eligió la opción OTRO de un catálogo" y, de forma
    análoga, "campo obligatorio solo cuando otro campo booleano es
    verdadero" (p. ej. ``espesor_pared_mm`` cuando ``es_hueco`` es
    ``True``).
    """
    vacio = valor is None or (isinstance(valor, str) and not valor.strip())
    if condicion and vacio:
        raise ValueError(mensaje)
