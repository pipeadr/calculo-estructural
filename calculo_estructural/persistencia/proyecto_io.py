"""Guardar y abrir proyectos como JSON en disco.

Usa directamente la serialización nativa de Pydantic sobre el modelo
``Proyecto`` ya existente (``model_dump_json`` / ``model_validate``): no
se duplica ninguna estructura de datos, no se usa ``pickle`` ni nada que
guarde objetos Python directamente, y los nombres de campo del JSON son
exactamente los de los modelos (incluidas las unidades en el propio
nombre: ``_mm``, ``_in``, ``_mpa``, ``_kn``, ``_knm``).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from ..models import Proyecto
from ..models.proyecto import VERSION_FORMATO_ACTUAL
from ..validation import ResultadoValidacion, hay_errores, validar_proyecto
from .excepciones import (
    ArchivoNoEncontradoError,
    DatosInvalidosError,
    EscrituraError,
    JSONInvalidoError,
    LecturaError,
    VersionNoSoportadaError,
)

VERSIONES_SOPORTADAS: set[str] = {VERSION_FORMATO_ACTUAL}
"""Versiones de formato que esta versión de la aplicación sabe leer. Hoy
solo existe "1.0"; cuando el formato cambie, las versiones antiguas se
agregan aquí junto con su migración correspondiente (todavía no existe:
por ahora una versión no listada aquí simplemente se rechaza con
VersionNoSoportadaError, en vez de intentar adivinarla)."""


class ProyectoValidado(BaseModel):
    """Resultado de guardar o abrir un proyecto: el ``Proyecto`` en sí,
    junto con el reporte de validación cruzada (Etapa 2) corrido en el
    momento.

    La validación NUNCA impide guardar ni abrir — un proyecto incompleto
    o con errores se guarda y se vuelve a abrir igual, como cualquier
    "guardar avance"; el llamador decide qué hacer con el reporte (p. ej.
    la interfaz podría mostrar un aviso si ``tiene_errores`` es True).
    """

    proyecto: Proyecto
    resultados_validacion: list[ResultadoValidacion]

    @property
    def tiene_errores(self) -> bool:
        return hay_errores(self.resultados_validacion)


def guardar_proyecto(proyecto: Proyecto, ruta: str | Path) -> ProyectoValidado:
    """Guarda ``proyecto`` como JSON legible en ``ruta`` (crea el archivo
    o sobrescribe uno existente).

    Corre la validación cruzada de la Etapa 2 antes de escribir y la
    devuelve junto con el proyecto guardado; no bloquea el guardado de un
    proyecto incompleto o con errores.
    """
    ruta = Path(ruta)
    resultados = validar_proyecto(proyecto)
    contenido = proyecto.model_dump_json(indent=2)

    try:
        ruta.write_text(contenido, encoding="utf-8")
    except OSError as error:
        raise EscrituraError(ruta, error) from error

    return ProyectoValidado(proyecto=proyecto, resultados_validacion=resultados)


def cargar_proyecto(ruta: str | Path) -> ProyectoValidado:
    """Abre un proyecto guardado por ``guardar_proyecto``.

    Se valida en orden, cada paso con su propio tipo de error (todos
    heredan de ``ProyectoIOError``), para que el mensaje mostrado sea
    específico en vez de un error genérico:

    1. El archivo existe y se puede leer -> ``ArchivoNoEncontradoError`` / ``LecturaError``
    2. El contenido es JSON sintácticamente válido -> ``JSONInvalidoError``
    3. La versión de formato es reconocida -> ``VersionNoSoportadaError``
    4. El contenido cumple el esquema de ``Proyecto`` (incluye campos
       obligatorios faltantes y tipos incorrectos) -> ``DatosInvalidosError``

    Si las cuatro pasan, se corre también la validación cruzada de la
    Etapa 2 sobre el proyecto reconstruido, igual que al guardar.
    """
    ruta = Path(ruta)

    try:
        texto = ruta.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ArchivoNoEncontradoError(ruta) from error
    except OSError as error:
        raise LecturaError(ruta, error) from error

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise JSONInvalidoError(ruta, error) from error

    if isinstance(datos, dict):
        version_encontrada = datos.get("version_formato")
        if version_encontrada not in VERSIONES_SOPORTADAS:
            raise VersionNoSoportadaError(ruta, version_encontrada, VERSIONES_SOPORTADAS)

    try:
        proyecto = Proyecto.model_validate(datos)
    except ValidationError as error:
        raise DatosInvalidosError(ruta, error) from error

    resultados = validar_proyecto(proyecto)
    return ProyectoValidado(proyecto=proyecto, resultados_validacion=resultados)
