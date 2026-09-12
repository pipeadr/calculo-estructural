"""Formulario del elemento de concreto."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QLineEdit, QVBoxLayout, QWidget

from ...models import ElementoConcreto, TipoElementoConcreto
from .base_form import SeccionFormBase, señales_bloqueadas


def _spin(sufijo: str, maximo: float, decimales: int = 2, valor_inicial: float = 1.0) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.01, maximo)
    spin.setDecimals(decimales)
    spin.setSuffix(sufijo)
    spin.setKeyboardTracking(False)
    spin.setValue(valor_inicial)
    return spin


class ElementoConcretoForm(SeccionFormBase):
    """Formulario de ``ElementoConcreto``."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_tipo = QComboBox()
        for tipo in TipoElementoConcreto:
            self.combo_tipo.addItem(tipo.value, tipo)
        self.combo_tipo.currentIndexChanged.connect(self._on_tipo_cambiado)
        self.combo_tipo.currentIndexChanged.connect(lambda _i: self._intentar_aplicar())

        self.campo_tipo_otro = QLineEdit()
        self.campo_tipo_otro.setEnabled(False)
        self.campo_tipo_otro.setPlaceholderText("Descripción (obligatorio si el tipo es OTRO)")
        self.campo_tipo_otro.editingFinished.connect(self._intentar_aplicar)

        self.spin_largo = _spin(" mm", 100000.0, valor_inicial=600.0)
        self.spin_ancho = _spin(" mm", 100000.0, valor_inicial=600.0)
        self.spin_altura = _spin(" mm", 100000.0, valor_inicial=500.0)
        self.spin_fc = _spin(" MPa", 5000.0, decimales=1, valor_inicial=21.0)
        for spin in (self.spin_largo, self.spin_ancho, self.spin_altura, self.spin_fc):
            spin.valueChanged.connect(lambda _valor: self._intentar_aplicar())

        formulario = QFormLayout()
        formulario.addRow("Tipo de elemento:", self.combo_tipo)
        formulario.addRow("Si es OTRO, especifique:", self.campo_tipo_otro)
        formulario.addRow("Largo (mm):", self.spin_largo)
        formulario.addRow("Ancho (mm):", self.spin_ancho)
        formulario.addRow("Altura o espesor (mm):", self.spin_altura)
        formulario.addRow("f'c (MPa):", self.spin_fc)

        layout = QVBoxLayout(self)
        layout.addWidget(self.banner_error)
        layout.addLayout(formulario)
        layout.addStretch(1)

    def _on_tipo_cambiado(self, _indice: int) -> None:
        self.campo_tipo_otro.setEnabled(self.combo_tipo.currentData() == TipoElementoConcreto.OTRO)

    def _construir_modelo(self) -> ElementoConcreto:
        return ElementoConcreto(
            tipo_elemento=self.combo_tipo.currentData(),
            tipo_elemento_otro=self.campo_tipo_otro.text().strip() or None,
            largo_mm=self.spin_largo.value(),
            ancho_mm=self.spin_ancho.value(),
            altura_mm=self.spin_altura.value(),
            fc_mpa=self.spin_fc.value(),
        )

    def cargar_datos(self, instancia: ElementoConcreto | None) -> None:
        widgets = (self.combo_tipo, self.campo_tipo_otro, self.spin_largo, self.spin_ancho, self.spin_altura, self.spin_fc)
        with señales_bloqueadas(*widgets):
            if instancia is None:
                self.combo_tipo.setCurrentIndex(0)
                self.campo_tipo_otro.setText("")
                self.campo_tipo_otro.setEnabled(False)
                self.spin_largo.setValue(600.0)
                self.spin_ancho.setValue(600.0)
                self.spin_altura.setValue(500.0)
                self.spin_fc.setValue(21.0)
            else:
                indice = self.combo_tipo.findData(instancia.tipo_elemento)
                self.combo_tipo.setCurrentIndex(indice if indice >= 0 else 0)
                self.campo_tipo_otro.setText(instancia.tipo_elemento_otro or "")
                self.campo_tipo_otro.setEnabled(instancia.tipo_elemento == TipoElementoConcreto.OTRO)
                self.spin_largo.setValue(instancia.largo_mm)
                self.spin_ancho.setValue(instancia.ancho_mm)
                self.spin_altura.setValue(instancia.altura_mm)
                self.spin_fc.setValue(instancia.fc_mpa)
        self._ocultar_error()
