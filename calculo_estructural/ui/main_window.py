"""Ventana principal: menú Archivo, panel de datos (7 formularios),
área de visualización (planta/sección), panel de validaciones y barra de
estado.

No calcula ni valida nada por su cuenta: delega todo en ``EstadoProyecto``
(persistencia + validación cruzada) y en ``dibujo`` (las figuras). Su
único trabajo es conectar señales entre los formularios, el estado y las
vistas.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QWidget,
)

from ..dibujo import dibujar_seccion_transversal, dibujar_vista_planta
from ..persistencia import ProyectoIOError
from .dialogs import NuevoProyectoDialog
from .estado_proyecto import EstadoProyecto, GuardadoBloqueadoPorErroresError
from .forms import (
    CargasForm,
    DatosGeneralesForm,
    ElementoConcretoForm,
    PerfilMetalicoForm,
    PernosForm,
    PlacaBaseForm,
    SoldaduraForm,
)
from .widgets import LienzoMatplotlib, PanelValidaciones

_FILTRO_ARCHIVOS = "Proyectos de cálculo estructural (*.json)"


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cálculo Estructural")
        self.resize(1280, 800)

        self.estado = EstadoProyecto(self)
        self.estado.proyecto_cambiado.connect(self._refrescar_todo)

        self._crear_menu()
        self._crear_widgets_centrales()
        self._crear_panel_validaciones()
        self._crear_barra_estado()

        self._refrescar_todo()

    # --- construcción de la interfaz -----------------------------------

    def _crear_menu(self) -> None:
        menu_archivo = self.menuBar().addMenu("&Archivo")

        accion_nuevo = QAction("&Nuevo proyecto", self)
        accion_nuevo.setShortcut(QKeySequence.StandardKey.New)
        accion_nuevo.triggered.connect(self._nuevo)
        menu_archivo.addAction(accion_nuevo)

        accion_abrir = QAction("&Abrir proyecto...", self)
        accion_abrir.setShortcut(QKeySequence.StandardKey.Open)
        accion_abrir.triggered.connect(lambda: self._abrir())
        menu_archivo.addAction(accion_abrir)

        menu_archivo.addSeparator()

        accion_guardar = QAction("&Guardar", self)
        accion_guardar.setShortcut(QKeySequence.StandardKey.Save)
        accion_guardar.triggered.connect(self._guardar)
        menu_archivo.addAction(accion_guardar)

        accion_guardar_como = QAction("Guardar &como...", self)
        accion_guardar_como.setShortcut(QKeySequence.StandardKey.SaveAs)
        accion_guardar_como.triggered.connect(lambda: self._guardar_como())
        menu_archivo.addAction(accion_guardar_como)

        menu_archivo.addSeparator()

        accion_cerrar = QAction("&Cerrar", self)
        accion_cerrar.setShortcut(QKeySequence.StandardKey.Close)
        accion_cerrar.triggered.connect(self.close)
        menu_archivo.addAction(accion_cerrar)

        self.acciones_archivo = {
            "nuevo": accion_nuevo,
            "abrir": accion_abrir,
            "guardar": accion_guardar,
            "guardar_como": accion_guardar_como,
            "cerrar": accion_cerrar,
        }

    def _crear_widgets_centrales(self) -> None:
        self.form_datos_generales = DatosGeneralesForm()
        self.form_placa_base = PlacaBaseForm()
        self.form_perfil_metalico = PerfilMetalicoForm()
        self.form_elemento_concreto = ElementoConcretoForm()
        self.form_pernos = PernosForm()
        self.form_soldadura = SoldaduraForm()
        self.form_cargas = CargasForm()

        self.formularios_por_seccion = {
            "placa_base": self.form_placa_base,
            "perfil_metalico": self.form_perfil_metalico,
            "elemento_concreto": self.form_elemento_concreto,
            "pernos": self.form_pernos,
            "soldadura": self.form_soldadura,
            "cargas": self.form_cargas,
        }
        for nombre_campo, formulario in self.formularios_por_seccion.items():
            formulario.datos_aplicados.connect(
                lambda instancia, nombre=nombre_campo: self.estado.actualizar_seccion(nombre, instancia)
            )
        self.form_datos_generales.datos_aplicados.connect(self.estado.actualizar_metadatos)

        self.tabs_datos = QTabWidget()
        self.tabs_datos.addTab(self._con_scroll(self.form_datos_generales), "Datos generales")
        self.tabs_datos.addTab(self._con_scroll(self.form_placa_base), "Placa base")
        self.tabs_datos.addTab(self._con_scroll(self.form_perfil_metalico), "Perfil metálico")
        self.tabs_datos.addTab(self._con_scroll(self.form_elemento_concreto), "Elemento de concreto")
        self.tabs_datos.addTab(self._con_scroll(self.form_pernos), "Pernos")
        self.tabs_datos.addTab(self._con_scroll(self.form_soldadura), "Soldadura")
        self.tabs_datos.addTab(self._con_scroll(self.form_cargas), "Cargas y momentos")

        self.lienzo_planta = LienzoMatplotlib()
        self.lienzo_seccion = LienzoMatplotlib()
        self.tabs_visualizacion = QTabWidget()
        self.tabs_visualizacion.addTab(self.lienzo_planta, "Vista en planta")
        self.tabs_visualizacion.addTab(self.lienzo_seccion, "Sección transversal")

        divisor = QSplitter()
        divisor.addWidget(self.tabs_datos)
        divisor.addWidget(self.tabs_visualizacion)
        divisor.setStretchFactor(0, 1)
        divisor.setStretchFactor(1, 2)
        self.setCentralWidget(divisor)

    @staticmethod
    def _con_scroll(widget: QWidget) -> QScrollArea:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)
        return area

    def _crear_panel_validaciones(self) -> None:
        self.panel_validaciones = PanelValidaciones()
        dock = QDockWidget("Validaciones", self)
        dock.setWidget(self.panel_validaciones)
        dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        self.dock_validaciones = dock

    def _crear_barra_estado(self) -> None:
        self.etiqueta_resumen_validacion = QLabel()
        self.statusBar().addPermanentWidget(self.etiqueta_resumen_validacion)

    # --- refresco reactivo (conectado a EstadoProyecto.proyecto_cambiado) --

    def _refrescar_todo(self) -> None:
        proyecto = self.estado.proyecto
        self.form_datos_generales.cargar_datos(proyecto.metadatos)
        for nombre_campo, formulario in self.formularios_por_seccion.items():
            formulario.cargar_datos(getattr(proyecto, nombre_campo))
        self._refrescar_dibujos()
        self._refrescar_validaciones()
        self._actualizar_titulo()

    def _refrescar_dibujos(self) -> None:
        proyecto = self.estado.proyecto
        self.lienzo_planta.mostrar_figura(dibujar_vista_planta(proyecto))
        self.lienzo_seccion.mostrar_figura(dibujar_seccion_transversal(proyecto))

    def _refrescar_validaciones(self) -> None:
        resultados = self.estado.resultados_validacion()
        self.panel_validaciones.actualizar(resultados)
        self.etiqueta_resumen_validacion.setText(self.panel_validaciones.resumen_por_estado(resultados))

    def _actualizar_titulo(self) -> None:
        archivo = self.estado.ruta_actual.name if self.estado.ruta_actual else "sin guardar"
        marca = " *" if self.estado.modificado else ""
        self.setWindowTitle(f"Cálculo Estructural — {self.estado.proyecto.metadatos.nombre} ({archivo}){marca}")

    # --- acciones de Archivo ---------------------------------------------

    def _nuevo(self) -> None:
        dialogo = NuevoProyectoDialog(self)
        if dialogo.exec() != NuevoProyectoDialog.DialogCode.Accepted:
            return
        nombre, autor, descripcion = dialogo.valores()
        self.estado.nuevo_proyecto(nombre=nombre or "Proyecto sin título", autor=autor, descripcion=descripcion)
        self.statusBar().showMessage("Nuevo proyecto creado", 5000)

    def _abrir(self, ruta: Path | None = None) -> None:
        """Abre ``ruta``; si es ``None``, primero la pide con un diálogo
        de archivo (así se puede probar sin diálogo real, pasando la
        ruta directamente)."""
        if ruta is None:
            texto_ruta, _ = QFileDialog.getOpenFileName(self, "Abrir proyecto", "", _FILTRO_ARCHIVOS)
            if not texto_ruta:
                return
            ruta = Path(texto_ruta)

        try:
            self.estado.abrir(ruta)
        except ProyectoIOError as error:
            QMessageBox.critical(self, "Error al abrir el proyecto", str(error))
            return
        self.statusBar().showMessage(f"Proyecto abierto desde {ruta}", 5000)

    def _guardar(self) -> None:
        if self.estado.ruta_actual is None:
            self._guardar_como()
            return
        self._ejecutar_guardado(self.estado.ruta_actual)

    def _guardar_como(self, ruta: Path | None = None) -> None:
        """Guarda en ``ruta``; si es ``None``, primero la pide con un
        diálogo de archivo (mismo patrón que ``_abrir``)."""
        if ruta is None:
            texto_ruta, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto como", "", _FILTRO_ARCHIVOS)
            if not texto_ruta:
                return
            ruta = Path(texto_ruta)
        self._ejecutar_guardado(ruta)

    def _ejecutar_guardado(self, ruta: Path) -> None:
        try:
            self.estado.guardar_como(ruta)
        except GuardadoBloqueadoPorErroresError as error:
            mensajes = "\n".join(f"- {r.mensaje}" for r in error.resultados_bloqueantes)
            QMessageBox.warning(
                self,
                "No se puede guardar",
                f"Hay {len(error.resultados_bloqueantes)} error(es) que deben corregirse antes de guardar:\n\n{mensajes}",
            )
            return
        except ProyectoIOError as error:
            QMessageBox.critical(self, "Error al guardar el proyecto", str(error))
            return
        self._actualizar_titulo()
        self.statusBar().showMessage(f"Proyecto guardado en {ruta}", 5000)

    # --- cierre ------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.estado.modificado:
            event.accept()
            return

        respuesta = QMessageBox.question(
            self,
            "Cambios sin guardar",
            "Hay cambios sin guardar. ¿Deseas guardarlos antes de cerrar?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        )
        if respuesta == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        if respuesta == QMessageBox.StandardButton.Save:
            self._guardar()
            if self.estado.modificado:
                # Seguía sin guardar (se canceló el diálogo de ruta, o
                # el guardado quedó bloqueado por errores): no cerrar.
                event.ignore()
                return
        event.accept()
