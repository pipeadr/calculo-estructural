"""Pruebas de la ventana principal.

Los diálogos modales (QDialog.exec, QMessageBox.*) bloquean con su propio
event loop si se llaman de verdad — se parchean con monkeypatch en cada
prueba que los dispara, para no colgar la suite. Ninguna prueba llama a
`.show()` ni a `app.exec()`.
"""

from __future__ import annotations

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QMessageBox

from calculo_estructural.persistencia import guardar_proyecto
from calculo_estructural.ui.dialogs import NuevoProyectoDialog
from calculo_estructural.ui.main_window import MainWindow
from calculo_estructural.validation import EstadoValidacion

# --- Caso: crear ventana --------------------------------------------------


def test_main_window_se_crea_sin_errores(qapp):
    ventana = MainWindow()

    assert ventana.centralWidget() is not None
    assert ventana.tabs_datos.count() == 7
    assert ventana.tabs_visualizacion.count() == 2
    assert ventana.dock_validaciones is not None
    assert set(ventana.acciones_archivo) == {"nuevo", "abrir", "guardar", "guardar_como", "cerrar"}


def test_main_window_arranca_con_un_proyecto_en_blanco_y_dibuja_algo(qapp):
    ventana = MainWindow()

    assert ventana.estado.proyecto.placa_base is None
    assert len(ventana.lienzo_planta.canvas.figure.axes) == 1
    assert len(ventana.lienzo_seccion.canvas.figure.axes) == 1


# --- Caso: crear proyecto (desde el menú, con el diálogo parcheado) ------


def test_main_window_nuevo_via_menu_crea_proyecto_en_blanco(qapp, monkeypatch):
    ventana = MainWindow()
    monkeypatch.setattr(NuevoProyectoDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    monkeypatch.setattr(NuevoProyectoDialog, "valores", lambda self: ("Proyecto de prueba", "Ana", "desc"))

    ventana._nuevo()

    assert ventana.estado.proyecto.metadatos.nombre == "Proyecto de prueba"
    assert ventana.estado.proyecto.metadatos.autor == "Ana"
    assert ventana.estado.proyecto.placa_base is None


# --- Caso: guardar proyecto desde la interfaz ----------------------------


def test_main_window_guardar_como_con_ruta_explicita_crea_archivo(qapp, tmp_path):
    ventana = MainWindow()
    ruta = tmp_path / "proyecto.json"

    ventana._guardar_como(ruta)

    assert ruta.exists()
    assert ventana.estado.ruta_actual == ruta
    assert "*" not in ventana.windowTitle()


def test_main_window_guardar_con_errores_muestra_advertencia_y_no_guarda(qapp, proyecto_ejemplo, tmp_path, monkeypatch):
    ventana = MainWindow()
    proyecto_con_error = proyecto_ejemplo.model_copy(deep=True)
    proyecto_con_error.pernos = proyecto_con_error.pernos.model_copy(update={"diametro_in": 5.0})
    ventana.estado._proyecto = proyecto_con_error
    ruta = tmp_path / "no_deberia_crearse.json"

    avisos = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: avisos.append(args) or QMessageBox.StandardButton.Ok)

    ventana._guardar_como(ruta)

    assert not ruta.exists()
    assert len(avisos) == 1


# --- Caso: abrir proyecto desde la interfaz ------------------------------


def test_main_window_abrir_con_ruta_explicita_carga_proyecto(qapp, proyecto_ejemplo, tmp_path):
    ruta = tmp_path / "existente.json"
    guardar_proyecto(proyecto_ejemplo, ruta)
    ventana = MainWindow()

    ventana._abrir(ruta)

    assert ventana.estado.proyecto.metadatos.nombre == proyecto_ejemplo.metadatos.nombre
    assert ventana.form_placa_base.tabla_perforaciones.cantidad() == len(proyecto_ejemplo.placa_base.perforaciones)


def test_main_window_abrir_archivo_inexistente_muestra_error_critico(qapp, tmp_path, monkeypatch):
    ventana = MainWindow()
    errores = []
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: errores.append(args) or QMessageBox.StandardButton.Ok)

    ventana._abrir(tmp_path / "no_existe.json")

    assert len(errores) == 1


# --- Caso: actualizar formularios y dibujos al editar ---------------------


def test_main_window_editar_formulario_actualiza_estado_dibujos_y_validaciones(qapp, placa_base_ejemplo):
    ventana = MainWindow()

    ventana.form_placa_base.cargar_datos(placa_base_ejemplo)
    ventana.form_placa_base.spin_largo.setValue(999.0)

    assert ventana.estado.proyecto.placa_base.largo_mm == 999.0
    assert ventana.estado.modificado
    # El dibujo se debe haber regenerado a partir del proyecto actualizado.
    assert len(ventana.lienzo_planta.canvas.figure.axes) == 1


# --- Caso: mostrar errores de validación ----------------------------------


def test_main_window_muestra_errores_de_validacion_en_el_panel(qapp, proyecto_ejemplo):
    ventana = MainWindow()
    proyecto_con_error = proyecto_ejemplo.model_copy(deep=True)
    proyecto_con_error.pernos = proyecto_con_error.pernos.model_copy(update={"diametro_in": 5.0})

    ventana.estado._proyecto = proyecto_con_error
    ventana.estado.proyecto_cambiado.emit()

    filas_error = [
        fila
        for fila in range(ventana.panel_validaciones.cantidad_filas())
        if ventana.panel_validaciones.texto_de(fila, 0) == EstadoValidacion.ERROR.value
    ]
    assert len(filas_error) >= 1
    assert "0 error" not in ventana.etiqueta_resumen_validacion.text()


# --- Cierre de la ventana --------------------------------------------------


def test_close_event_sin_cambios_acepta_cerrar(qapp):
    ventana = MainWindow()
    evento = QCloseEvent()

    ventana.closeEvent(evento)

    assert evento.isAccepted()


def test_close_event_con_cambios_y_descartar_acepta_cerrar(qapp, cargas_ejemplo, monkeypatch):
    ventana = MainWindow()
    ventana.estado.actualizar_seccion("cargas", cargas_ejemplo)
    assert ventana.estado.modificado

    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Discard)
    evento = QCloseEvent()

    ventana.closeEvent(evento)

    assert evento.isAccepted()


def test_close_event_con_cambios_y_cancelar_no_cierra(qapp, cargas_ejemplo, monkeypatch):
    ventana = MainWindow()
    ventana.estado.actualizar_seccion("cargas", cargas_ejemplo)

    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Cancel)
    evento = QCloseEvent()

    ventana.closeEvent(evento)

    assert not evento.isAccepted()
