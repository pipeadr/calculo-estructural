"""Formulario de los pernos de anclaje.

``cantidad`` no se muestra como campo editable: se deriva del número de
filas de la tabla de posiciones (etiqueta de solo lectura), igual que
``numero_perforaciones`` en el formulario de la placa base.
"""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from ...models import PosicionPerno, Pernos, TipoGradoPerno
from ..widgets import TablaCoordenadas
from .base_form import SeccionFormBase, señales_bloqueadas


def _spin(sufijo: str, maximo: float, decimales: int, valor_inicial: float) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.001, maximo)
    spin.setDecimals(decimales)
    spin.setSuffix(sufijo)
    spin.setKeyboardTracking(False)
    spin.setValue(valor_inicial)
    return spin


class PernosForm(SeccionFormBase):
    """Formulario de ``Pernos``."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.spin_diametro = _spin(" in", 10.0, 3, 0.75)
        self.spin_longitud = _spin(" mm", 100000.0, 2, 400.0)
        self.spin_embebido = _spin(" mm", 100000.0, 2, 300.0)
        for spin in (self.spin_diametro, self.spin_longitud, self.spin_embebido):
            spin.valueChanged.connect(lambda _valor: self._intentar_aplicar())

        self.combo_tipo_grado = QComboBox()
        for tipo in TipoGradoPerno:
            self.combo_tipo_grado.addItem(tipo.value, tipo)
        self.combo_tipo_grado.currentIndexChanged.connect(self._on_tipo_grado_cambiado)
        self.combo_tipo_grado.currentIndexChanged.connect(lambda _i: self._intentar_aplicar())

        self.campo_tipo_grado_otro = QLineEdit()
        self.campo_tipo_grado_otro.setEnabled(False)
        self.campo_tipo_grado_otro.setPlaceholderText("Designación (obligatorio si el tipo es OTRO)")
        self.campo_tipo_grado_otro.editingFinished.connect(self._intentar_aplicar)

        self.etiqueta_cantidad = QLabel()
        self.tabla_posiciones = TablaCoordenadas()
        self.tabla_posiciones.puntos_cambiados.connect(self._on_tabla_cambiada)

        formulario = QFormLayout()
        formulario.addRow("Diámetro (in):", self.spin_diametro)
        formulario.addRow("Longitud (mm):", self.spin_longitud)
        formulario.addRow("Tipo/grado:", self.combo_tipo_grado)
        formulario.addRow("Si es OTRO, especifique:", self.campo_tipo_grado_otro)
        formulario.addRow("Profundidad de embebido (mm):", self.spin_embebido)

        layout = QVBoxLayout(self)
        layout.addWidget(self.banner_error)
        layout.addLayout(formulario)
        layout.addWidget(self.etiqueta_cantidad)
        layout.addWidget(self.tabla_posiciones)

        self._actualizar_etiqueta_cantidad()

    def _on_tipo_grado_cambiado(self, _indice: int) -> None:
        self.campo_tipo_grado_otro.setEnabled(self.combo_tipo_grado.currentData() == TipoGradoPerno.OTRO)

    def _actualizar_etiqueta_cantidad(self) -> None:
        self.etiqueta_cantidad.setText(f"Cantidad de pernos: {self.tabla_posiciones.cantidad()} (según la tabla)")

    def _on_tabla_cambiada(self) -> None:
        self._actualizar_etiqueta_cantidad()
        self._intentar_aplicar()

    def _construir_modelo(self) -> Pernos:
        puntos = self.tabla_posiciones.obtener_puntos()
        return Pernos(
            cantidad=len(puntos),
            diametro_in=self.spin_diametro.value(),
            longitud_mm=self.spin_longitud.value(),
            tipo_grado=self.combo_tipo_grado.currentData(),
            tipo_grado_otro=self.campo_tipo_grado_otro.text().strip() or None,
            profundidad_embebido_mm=self.spin_embebido.value(),
            posiciones=[PosicionPerno(x_mm=x, y_mm=y) for x, y in puntos],
        )

    def cargar_datos(self, instancia: Pernos | None) -> None:
        widgets = (self.spin_diametro, self.spin_longitud, self.spin_embebido, self.combo_tipo_grado, self.campo_tipo_grado_otro)
        with señales_bloqueadas(*widgets):
            if instancia is None:
                self.spin_diametro.setValue(0.75)
                self.spin_longitud.setValue(400.0)
                self.spin_embebido.setValue(300.0)
                self.combo_tipo_grado.setCurrentIndex(0)
                self.campo_tipo_grado_otro.setText("")
                self.campo_tipo_grado_otro.setEnabled(False)
                self.tabla_posiciones.cargar_puntos([])
            else:
                self.spin_diametro.setValue(instancia.diametro_in)
                self.spin_longitud.setValue(instancia.longitud_mm)
                self.spin_embebido.setValue(instancia.profundidad_embebido_mm)
                indice = self.combo_tipo_grado.findData(instancia.tipo_grado)
                self.combo_tipo_grado.setCurrentIndex(indice if indice >= 0 else 0)
                self.campo_tipo_grado_otro.setText(instancia.tipo_grado_otro or "")
                self.campo_tipo_grado_otro.setEnabled(instancia.tipo_grado == TipoGradoPerno.OTRO)
                self.tabla_posiciones.cargar_puntos([(p.x_mm, p.y_mm) for p in instancia.posiciones])
        self._actualizar_etiqueta_cantidad()
        self._ocultar_error()
