"""Pruebas de ui.estado_proyecto (lógica pura: ninguna crea una ventana)."""

from __future__ import annotations

import pytest

from calculo_estructural.models import Cargas
from calculo_estructural.persistencia import ArchivoNoEncontradoError, guardar_proyecto
from calculo_estructural.ui.estado_proyecto import EstadoProyecto, GuardadoBloqueadoPorErroresError


def test_estado_proyecto_arranca_con_un_proyecto_en_blanco(qapp):
    estado = EstadoProyecto()

    assert estado.proyecto.metadatos.nombre
    assert estado.proyecto.placa_base is None
    assert estado.ruta_actual is None
    assert not estado.modificado


def test_nuevo_proyecto_reemplaza_el_actual_y_emite_senal(qapp):
    estado = EstadoProyecto()
    emitida = []
    estado.proyecto_cambiado.connect(lambda: emitida.append(True))

    estado.nuevo_proyecto(nombre="Mi proyecto", autor="Ana")

    assert estado.proyecto.metadatos.nombre == "Mi proyecto"
    assert estado.proyecto.metadatos.autor == "Ana"
    assert estado.proyecto.placa_base is None
    assert len(emitida) == 1


def test_actualizar_seccion_marca_modificado_y_emite_senal(qapp, cargas_ejemplo):
    estado = EstadoProyecto()
    emitida = []
    estado.proyecto_cambiado.connect(lambda: emitida.append(True))

    estado.actualizar_seccion("cargas", cargas_ejemplo)

    assert estado.proyecto.cargas == cargas_ejemplo
    assert estado.modificado
    assert len(emitida) == 1


def test_actualizar_metadatos_marca_modificado(qapp):
    estado = EstadoProyecto()
    nuevos_metadatos = estado.proyecto.metadatos.model_copy(update={"autor": "Nuevo autor"})

    estado.actualizar_metadatos(nuevos_metadatos)

    assert estado.proyecto.metadatos.autor == "Nuevo autor"
    assert estado.modificado


def test_guardar_sin_ruta_asignada_lanza_value_error(qapp):
    estado = EstadoProyecto()
    with pytest.raises(ValueError):
        estado.guardar()


def test_guardar_como_proyecto_en_blanco_no_esta_bloqueado(qapp, tmp_path):
    # Un proyecto recién creado no tiene ERROR (todo NO_VERIFICADO), así
    # que sí debe poder guardarse.
    estado = EstadoProyecto()
    ruta = tmp_path / "proyecto.json"

    estado.guardar_como(ruta)

    assert ruta.exists()
    assert estado.ruta_actual == ruta
    assert not estado.modificado


def test_guardar_como_con_errores_de_validacion_es_bloqueado(qapp, proyecto_ejemplo, tmp_path):
    estado = EstadoProyecto()
    proyecto_con_error = proyecto_ejemplo.model_copy(deep=True)
    proyecto_con_error.pernos = proyecto_con_error.pernos.model_copy(update={"diametro_in": 5.0})
    estado._proyecto = proyecto_con_error
    ruta = tmp_path / "no_deberia_crearse.json"

    with pytest.raises(GuardadoBloqueadoPorErroresError) as exc_info:
        estado.guardar_como(ruta)

    assert not ruta.exists()
    assert any(r.codigo == "PERNO_PERFORACION_DIAMETRO" for r in exc_info.value.resultados_bloqueantes)


def test_guardar_reutiliza_la_ruta_de_guardar_como(qapp, tmp_path):
    estado = EstadoProyecto()
    ruta = tmp_path / "proyecto.json"
    estado.guardar_como(ruta)

    estado.actualizar_seccion(
        "cargas",
        Cargas(axial_kn=-10, cortante_x_kn=0, cortante_y_kn=0, momento_x_knm=0, momento_y_knm=0, momento_z_knm=0),
    )
    estado.guardar()

    assert '"axial_kn": -10.0' in ruta.read_text(encoding="utf-8")


def test_abrir_actualiza_proyecto_ruta_y_emite_senal(qapp, proyecto_ejemplo, tmp_path):
    ruta = tmp_path / "existente.json"
    guardar_proyecto(proyecto_ejemplo, ruta)

    estado = EstadoProyecto()
    emitida = []
    estado.proyecto_cambiado.connect(lambda: emitida.append(True))

    estado.abrir(ruta)

    assert estado.proyecto.metadatos.nombre == proyecto_ejemplo.metadatos.nombre
    assert estado.ruta_actual == ruta
    assert not estado.modificado
    assert len(emitida) == 1


def test_abrir_archivo_inexistente_propaga_el_error(qapp, tmp_path):
    estado = EstadoProyecto()
    with pytest.raises(ArchivoNoEncontradoError):
        estado.abrir(tmp_path / "no_existe.json")
