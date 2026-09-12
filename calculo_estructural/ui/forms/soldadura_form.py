"""Formulario de la soldadura."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QLineEdit, QVBoxLayout, QWidget

from ...models import Soldadura, TipoSoldadura
from .base_form import SeccionFormBase, señales_bloqueadas


def _spin_mm(valor_inicial: float) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.01, 100000.0)
    spin.setDecimals(2)
    spin.setSuffix(" mm")
    spin.setKeyboardTracking(False)
    spin.setValue(valor_inicial)
    return spin


class SoldaduraForm(SeccionFormBase):
    """Formulario de ``Soldadura``.

    ``simbolo`` es texto libre (p. ej. "Filete continuo, ambos lados");
    esta fase no dibuja el símbolo AWS real, solo lo registra como
    anotación (ver ``models.soldadura``).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_tipo = QComboBox()
        for tipo in TipoSoldadura:
            self.combo_tipo.addItem(tipo.value, tipo)
        self.combo_tipo.currentIndexChanged.connect(self._on_tipo_cambiado)
        self.combo_tipo.currentIndexChanged.connect(lambda _i: self._intentar_aplicar())

        self.campo_tipo_otro = QLineEdit()
        self.campo_tipo_otro.setEnabled(False)
        self.campo_tipo_otro.setPlaceholderText("Descripción (obligatorio si el tipo es OTRO)")
        self.campo_tipo_otro.editingFinished.connect(self._intentar_aplicar)

        self.campo_simbolo = QLineEdit("Filete continuo, ambos lados")
        self.campo_simbolo.editingFinished.connect(self._intentar_aplicar)

        self.spin_espesor = _spin_mm(8.0)
        self.spin_longitud = _spin_mm(200.0)
        for spin in (self.spin_espesor, self.spin_longitud):
            spin.valueChanged.connect(lambda _valor: self._intentar_aplicar())

        formulario = QFormLayout()
        formulario.addRow("Tipo de soldadura:", self.combo_tipo)
        formulario.addRow("Si es OTRO, especifique:", self.campo_tipo_otro)
        formulario.addRow("Símbolo/anotación:", self.campo_simbolo)
        formulario.addRow("Espesor de garganta/pata (mm):", self.spin_espesor)
        formulario.addRow("Longitud (mm):", self.spin_longitud)

        layout = QVBoxLayout(self)
        layout.addWidget(self.banner_error)
        layout.addLayout(formulario)
        layout.addStretch(1)

    def _on_tipo_cambiado(self, _indice: int) -> None:
        self.campo_tipo_otro.setEnabled(self.combo_tipo.currentData() == TipoSoldadura.OTRO)

    def _construir_modelo(self) -> Soldadura:
        return Soldadura(
            tipo_soldadura=self.combo_tipo.currentData(),
            tipo_soldadura_otro=self.campo_tipo_otro.text().strip() or None,
            simbolo=self.campo_simbolo.text(),
            espesor_mm=self.spin_espesor.value(),
            longitud_mm=self.spin_longitud.value(),
        )

    def cargar_datos(self, instancia: Soldadura | None) -> None:
        widgets = (self.combo_tipo, self.campo_tipo_otro, self.campo_simbolo, self.spin_espesor, self.spin_longitud)
        with señales_bloqueadas(*widgets):
            if instancia is None:
                self.combo_tipo.setCurrentIndex(0)
                self.campo_tipo_otro.setText("")
                self.campo_tipo_otro.setEnabled(False)
                self.campo_simbolo.setText("Filete continuo, ambos lados")
                self.spin_espesor.setValue(8.0)
                self.spin_longitud.setValue(200.0)
            else:
                indice = self.combo_tipo.findData(instancia.tipo_soldadura)
                self.combo_tipo.setCurrentIndex(indice if indice >= 0 else 0)
                self.campo_tipo_otro.setText(instancia.tipo_soldadura_otro or "")
                self.campo_tipo_otro.setEnabled(instancia.tipo_soldadura == TipoSoldadura.OTRO)
                self.campo_simbolo.setText(instancia.simbolo)
                self.spin_espesor.setValue(instancia.espesor_mm)
                self.spin_longitud.setValue(instancia.longitud_mm)
        self._ocultar_error()
