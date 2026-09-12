"""Formulario de la placa base.

``numero_perforaciones`` no se muestra como campo editable: se deriva
del número de filas de la tabla de perforaciones (etiqueta de solo
lectura), para eliminar de raíz la posibilidad de que quede
desincronizado con la lista real de coordenadas.
"""

from __future__ import annotations

from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from ...models import Perforacion, PlacaBase, TipoAcero
from ..widgets import TablaCoordenadas
from .base_form import CamposMaterial, SeccionFormBase, señales_bloqueadas


def _spin_dimension_mm(valor_inicial: float = 1.0) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.01, 100000.0)
    spin.setDecimals(2)
    spin.setSuffix(" mm")
    spin.setKeyboardTracking(False)
    spin.setValue(valor_inicial)
    return spin


class PlacaBaseForm(SeccionFormBase):
    """Formulario de ``PlacaBase``: dimensiones, material y perforaciones."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.spin_largo = _spin_dimension_mm(300.0)
        self.spin_ancho = _spin_dimension_mm(300.0)
        self.spin_espesor = _spin_dimension_mm(20.0)
        for spin in (self.spin_largo, self.spin_ancho, self.spin_espesor):
            spin.valueChanged.connect(lambda _valor: self._intentar_aplicar())

        self.campos_material = CamposMaterial()
        self.campos_material.valores_cambiados.connect(self._intentar_aplicar)

        self.spin_diametro_perforacion = QDoubleSpinBox()
        self.spin_diametro_perforacion.setRange(0.01, 10.0)
        self.spin_diametro_perforacion.setDecimals(3)
        self.spin_diametro_perforacion.setSuffix(" in")
        self.spin_diametro_perforacion.setKeyboardTracking(False)
        self.spin_diametro_perforacion.setValue(1.0)
        self.spin_diametro_perforacion.valueChanged.connect(lambda _valor: self._intentar_aplicar())

        self.etiqueta_cantidad = QLabel()
        self.tabla_perforaciones = TablaCoordenadas()
        self.tabla_perforaciones.puntos_cambiados.connect(self._on_tabla_cambiada)

        grupo_dimensiones = QGroupBox("Dimensiones")
        formulario_dim = QFormLayout(grupo_dimensiones)
        formulario_dim.addRow("Largo (mm):", self.spin_largo)
        formulario_dim.addRow("Ancho (mm):", self.spin_ancho)
        formulario_dim.addRow("Espesor (mm):", self.spin_espesor)

        grupo_material = QGroupBox("Material")
        layout_material = QVBoxLayout(grupo_material)
        layout_material.addWidget(self.campos_material)

        grupo_perforaciones = QGroupBox("Perforaciones")
        layout_perf = QVBoxLayout(grupo_perforaciones)
        formulario_perf = QFormLayout()
        formulario_perf.addRow("Diámetro de perforación (in):", self.spin_diametro_perforacion)
        layout_perf.addLayout(formulario_perf)
        layout_perf.addWidget(self.etiqueta_cantidad)
        layout_perf.addWidget(self.tabla_perforaciones)

        layout = QVBoxLayout(self)
        layout.addWidget(self.banner_error)
        layout.addWidget(grupo_dimensiones)
        layout.addWidget(grupo_material)
        layout.addWidget(grupo_perforaciones)

        self._actualizar_etiqueta_cantidad()

    def _actualizar_etiqueta_cantidad(self) -> None:
        self.etiqueta_cantidad.setText(f"Perforaciones: {self.tabla_perforaciones.cantidad()} (según la tabla)")

    def _on_tabla_cambiada(self) -> None:
        self._actualizar_etiqueta_cantidad()
        self._intentar_aplicar()

    def _construir_modelo(self) -> PlacaBase:
        puntos = self.tabla_perforaciones.obtener_puntos()
        return PlacaBase(
            largo_mm=self.spin_largo.value(),
            ancho_mm=self.spin_ancho.value(),
            espesor_mm=self.spin_espesor.value(),
            numero_perforaciones=len(puntos),
            diametro_perforacion_in=self.spin_diametro_perforacion.value(),
            perforaciones=[Perforacion(x_mm=x, y_mm=y) for x, y in puntos],
            **self.campos_material.valores(),
        )

    def cargar_datos(self, instancia: PlacaBase | None) -> None:
        with señales_bloqueadas(self.spin_largo, self.spin_ancho, self.spin_espesor, self.spin_diametro_perforacion):
            if instancia is None:
                self.spin_largo.setValue(300.0)
                self.spin_ancho.setValue(300.0)
                self.spin_espesor.setValue(20.0)
                self.spin_diametro_perforacion.setValue(1.0)
                self.campos_material.cargar(TipoAcero.A36, None, 250.0)
                self.tabla_perforaciones.cargar_puntos([])
            else:
                self.spin_largo.setValue(instancia.largo_mm)
                self.spin_ancho.setValue(instancia.ancho_mm)
                self.spin_espesor.setValue(instancia.espesor_mm)
                self.spin_diametro_perforacion.setValue(instancia.diametro_perforacion_in)
                self.campos_material.cargar(instancia.tipo_acero, instancia.tipo_acero_otro, instancia.fy_mpa)
                self.tabla_perforaciones.cargar_puntos([(p.x_mm, p.y_mm) for p in instancia.perforaciones])
        self._actualizar_etiqueta_cantidad()
        self._ocultar_error()
