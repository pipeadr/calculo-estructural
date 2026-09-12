"""Pruebas de guardar y abrir proyectos en JSON (Etapa 3)."""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from calculo_estructural.models import MetadatosProyecto, Proyecto
from calculo_estructural.persistencia import (
    ArchivoNoEncontradoError,
    DatosInvalidosError,
    EscrituraError,
    JSONInvalidoError,
    LecturaError,
    ProyectoValidado,
    VersionNoSoportadaError,
    cargar_proyecto,
    guardar_proyecto,
)

# --- Caso 1: guardar un proyecto válido ---------------------------------


def test_guardar_proyecto_valido_crea_el_archivo(tmp_path, proyecto_ejemplo):
    ruta = tmp_path / "proyecto.json"

    resultado = guardar_proyecto(proyecto_ejemplo, ruta)

    assert ruta.exists()
    assert isinstance(resultado, ProyectoValidado)
    assert not resultado.tiene_errores


def test_guardar_proyecto_produce_json_legible_con_version(tmp_path, proyecto_ejemplo):
    ruta = tmp_path / "proyecto.json"

    guardar_proyecto(proyecto_ejemplo, ruta)

    contenido = ruta.read_text(encoding="utf-8")
    datos = json.loads(contenido)  # falla si no fuera JSON válido
    assert datos["version_formato"] == "1.0"
    assert "placa_base" in datos
    assert "configuracion" in datos
    assert "\n" in contenido  # con indentación, no todo en una línea


def test_guardar_proyecto_incompleto_no_falla(tmp_path):
    # Guardar un avance a medio llenar (secciones en None) debe funcionar
    # igual: la validación cruzada no bloquea el guardado.
    ahora = datetime.now()
    proyecto_incompleto = Proyecto(
        metadatos=MetadatosProyecto(nombre="Incompleto", fecha_creacion=ahora, fecha_modificacion=ahora)
    )

    resultado = guardar_proyecto(proyecto_incompleto, tmp_path / "incompleto.json")

    assert (tmp_path / "incompleto.json").exists()
    assert not resultado.tiene_errores  # sin ERROR, aunque sí NO_VERIFICADO


def test_guardar_en_carpeta_inexistente_lanza_escritura_error(tmp_path, proyecto_ejemplo):
    ruta = tmp_path / "carpeta_que_no_existe" / "proyecto.json"

    with pytest.raises(EscrituraError):
        guardar_proyecto(proyecto_ejemplo, ruta)


# --- Caso 2: abrir un proyecto válido ------------------------------------


def test_abrir_proyecto_valido(tmp_path, proyecto_ejemplo):
    ruta = tmp_path / "proyecto.json"
    guardar_proyecto(proyecto_ejemplo, ruta)

    resultado = cargar_proyecto(ruta)

    assert isinstance(resultado, ProyectoValidado)
    assert resultado.proyecto.metadatos.nombre == proyecto_ejemplo.metadatos.nombre
    assert not resultado.tiene_errores


# --- Caso 3: guardar y abrir un proyecto sin perder datos ----------------


def test_guardar_y_abrir_no_pierde_datos(tmp_path, proyecto_ejemplo):
    ruta = tmp_path / "proyecto.json"
    guardar_proyecto(proyecto_ejemplo, ruta)

    reabierto = cargar_proyecto(ruta).proyecto

    assert reabierto == proyecto_ejemplo
    # La unión discriminada de perfil_metalico debe reconstruirse como la
    # misma subclase concreta, no solo "igual como dict".
    assert type(reabierto.perfil_metalico) is type(proyecto_ejemplo.perfil_metalico)


# --- Caso 4: detectar un archivo JSON inválido ---------------------------


def test_abrir_archivo_no_encontrado(tmp_path):
    with pytest.raises(ArchivoNoEncontradoError):
        cargar_proyecto(tmp_path / "no_existe.json")


def test_abrir_una_carpeta_en_vez_de_un_archivo_lanza_lectura_error(tmp_path):
    carpeta = tmp_path / "esto_es_una_carpeta"
    carpeta.mkdir()

    with pytest.raises(LecturaError):
        cargar_proyecto(carpeta)


def test_abrir_json_con_sintaxis_invalida(tmp_path):
    ruta = tmp_path / "corrupto.json"
    ruta.write_text("{ esto no es JSON valido ][", encoding="utf-8")

    with pytest.raises(JSONInvalidoError):
        cargar_proyecto(ruta)


# --- Caso 5: detectar campos obligatorios faltantes ----------------------


def test_abrir_json_sin_campos_obligatorios(tmp_path):
    datos = {"version_formato": "1.0", "metadatos": {}}  # falta 'nombre' y las fechas
    ruta = tmp_path / "sin_nombre.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    with pytest.raises(DatosInvalidosError) as exc_info:
        cargar_proyecto(ruta)

    assert isinstance(exc_info.value.error_original, ValidationError)
    errores = exc_info.value.error_original.errors()
    assert any(err["type"] == "missing" for err in errores)


# --- Caso 6: detectar valores con tipos incorrectos ----------------------


def test_abrir_json_con_tipo_incorrecto(tmp_path, proyecto_ejemplo):
    datos = json.loads(proyecto_ejemplo.model_dump_json())
    datos["placa_base"]["largo_mm"] = "no-es-un-numero"
    ruta = tmp_path / "tipo_incorrecto.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    with pytest.raises(DatosInvalidosError) as exc_info:
        cargar_proyecto(ruta)

    errores = exc_info.value.error_original.errors()
    assert any("largo_mm" in ".".join(str(parte) for parte in err["loc"]) for err in errores)


# --- Caso 7: detectar una versión de proyecto no soportada ---------------


def test_abrir_json_con_version_no_soportada(tmp_path, proyecto_ejemplo):
    datos = json.loads(proyecto_ejemplo.model_dump_json())
    datos["version_formato"] = "99.0"
    ruta = tmp_path / "version_futura.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    with pytest.raises(VersionNoSoportadaError) as exc_info:
        cargar_proyecto(ruta)

    assert exc_info.value.version_encontrada == "99.0"
    assert exc_info.value.versiones_soportadas == {"1.0"}


def test_abrir_json_sin_declarar_version(tmp_path, proyecto_ejemplo):
    datos = json.loads(proyecto_ejemplo.model_dump_json())
    del datos["version_formato"]
    ruta = tmp_path / "sin_version.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    with pytest.raises(VersionNoSoportadaError) as exc_info:
        cargar_proyecto(ruta)

    assert exc_info.value.version_encontrada is None
