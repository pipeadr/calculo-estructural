"""Excepciones de la capa de persistencia de proyectos.

Todas heredan de ``ProyectoIOError``, para que quien llama a
``guardar_proyecto``/``cargar_proyecto`` pueda capturar una única clase
base y mostrar un mensaje amigable, o alguna de las subclases si necesita
distinguir el caso (por ejemplo, para ofrecer "elegir otro archivo" solo
cuando el archivo no existe).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError


class ProyectoIOError(Exception):
    """Error base de todas las excepciones de guardar/abrir proyectos."""


class ArchivoNoEncontradoError(ProyectoIOError):
    """La ruta indicada para abrir un proyecto no existe."""

    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta
        super().__init__(f"No se encontró el archivo de proyecto: {ruta}")


class LecturaError(ProyectoIOError):
    """El archivo existe pero no se pudo leer (permisos, es en realidad
    un directorio, codificación inesperada, etc.)."""

    def __init__(self, ruta: Path, error_original: OSError) -> None:
        self.ruta = ruta
        self.error_original = error_original
        super().__init__(f"No se pudo leer el archivo '{ruta}': {error_original}")


class EscrituraError(ProyectoIOError):
    """No se pudo escribir el archivo de proyecto (permisos, disco lleno,
    carpeta inexistente, etc.)."""

    def __init__(self, ruta: Path, error_original: OSError) -> None:
        self.ruta = ruta
        self.error_original = error_original
        super().__init__(f"No se pudo escribir el archivo '{ruta}': {error_original}")


class JSONInvalidoError(ProyectoIOError):
    """El archivo no contiene JSON sintácticamente válido."""

    def __init__(self, ruta: Path, error_original: json.JSONDecodeError) -> None:
        self.ruta = ruta
        self.error_original = error_original
        super().__init__(
            f"El archivo '{ruta}' no contiene JSON válido "
            f"(línea {error_original.lineno}, columna {error_original.colno}): "
            f"{error_original.msg}"
        )


class VersionNoSoportadaError(ProyectoIOError):
    """El archivo declara una versión de formato que esta versión de la
    aplicación no reconoce (o no declara ninguna)."""

    def __init__(
        self,
        ruta: Path,
        version_encontrada: str | None,
        versiones_soportadas: set[str],
    ) -> None:
        self.ruta = ruta
        self.version_encontrada = version_encontrada
        self.versiones_soportadas = versiones_soportadas
        soportadas = ", ".join(sorted(versiones_soportadas))
        detalle = (
            "no declara version_formato"
            if version_encontrada is None
            else f"declara version_formato='{version_encontrada}'"
        )
        super().__init__(
            f"El archivo '{ruta}' {detalle}, no reconocida por esta versión de "
            f"la aplicación (soportadas: {soportadas})."
        )


class DatosInvalidosError(ProyectoIOError):
    """El JSON es sintácticamente válido pero no cumple el esquema del
    proyecto: campos obligatorios faltantes, tipos incorrectos, valores
    fuera de rango, etc.

    Envuelve el ``ValidationError`` original de Pydantic en
    ``error_original`` — ``error_original.errors()`` trae el detalle
    campo por campo (incluye, entre otras cosas, si cada error es de tipo
    "missing" o de tipo incorrecto).
    """

    def __init__(self, ruta: Path, error_original: ValidationError) -> None:
        self.ruta = ruta
        self.error_original = error_original
        detalles = "; ".join(
            f"{'.'.join(str(parte) for parte in err['loc'])}: {err['msg']}"
            for err in error_original.errors()
        )
        super().__init__(f"El archivo '{ruta}' tiene datos inválidos: {detalles}")
