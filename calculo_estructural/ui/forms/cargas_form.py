"""Formulario de cargas y momentos.

Todas las fuerzas y momentos admiten valores negativos (no tienen un
mínimo en 0, a diferencia de las dimensiones): el signo lo interpreta la
convención que se documenta en ``convencion_signos`` (ver
``models.cargas`` y ``validation.cargas``).
"""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QLineEdit, QVBoxLayout, QWidget

from ...models import Cargas, TipoCombinacionCarga
from .base_form import SeccionFormBase, señales_bloqueadas


def _spin_carga(sufijo: str) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(-1_000_000.0, 1_000_000.0)
    spin.setDecimals(2)
    spin.setSuffix(sufijo)
    spin.setKeyboardTracking(False)
    spin.setValue(0.0)
    return spin


class CargasForm(SeccionFormBase):
    """Formulario de ``Cargas``."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.spin_axial = _spin_carga(" kN")
        self.spin_cortante_x = _spin_carga(" kN")
        self.spin_cortante_y = _spin_carga(" kN")
        self.spin_momento_x = _spin_carga(" kN·m")
        self.spin_momento_y = _spin_carga(" kN·m")
        self.spin_momento_z = _spin_carga(" kN·m")
        for spin in (
            self.spin_axial,
            self.spin_cortante_x,
            self.spin_cortante_y,
            self.spin_momento_x,
            self.spin_momento_y,
            self.spin_momento_z,
        ):
            spin.valueChanged.connect(lambda _valor: self._intentar_aplicar())

        self.combo_tipo_combinacion = QComboBox()
        for tipo in TipoCombinacionCarga:
            self.combo_tipo_combinacion.addItem(tipo.value, tipo)
        self.combo_tipo_combinacion.currentIndexChanged.connect(lambda _i: self._intentar_aplicar())

        self.campo_convencion_signos = QLineEdit()
        self.campo_convencion_signos.setPlaceholderText(
            "p.ej. 'Axial positivo = compresión; momentos según regla de la mano derecha'"
        )
        self.campo_convencion_signos.editingFinished.connect(self._intentar_aplicar)

        formulario = QFormLayout()
        formulario.addRow("Axial (kN):", self.spin_axial)
        formulario.addRow("Cortante X (kN):", self.spin_cortante_x)
        formulario.addRow("Cortante Y (kN):", self.spin_cortante_y)
        formulario.addRow("Momento X (kN·m):", self.spin_momento_x)
        formulario.addRow("Momento Y (kN·m):", self.spin_momento_y)
        formulario.addRow("Momento Z (kN·m):", self.spin_momento_z)
        formulario.addRow("Tipo de combinación:", self.combo_tipo_combinacion)
        formulario.addRow("Convención de signos:", self.campo_convencion_signos)

        layout = QVBoxLayout(self)
        layout.addWidget(self.banner_error)
        layout.addLayout(formulario)
        layout.addStretch(1)

    def _construir_modelo(self) -> Cargas:
        return Cargas(
            axial_kn=self.spin_axial.value(),
            cortante_x_kn=self.spin_cortante_x.value(),
            cortante_y_kn=self.spin_cortante_y.value(),
            momento_x_knm=self.spin_momento_x.value(),
            momento_y_knm=self.spin_momento_y.value(),
            momento_z_knm=self.spin_momento_z.value(),
            tipo_combinacion=self.combo_tipo_combinacion.currentData(),
            convencion_signos=self.campo_convencion_signos.text(),
        )

    def cargar_datos(self, instancia: Cargas | None) -> None:
        widgets = (
            self.spin_axial,
            self.spin_cortante_x,
            self.spin_cortante_y,
            self.spin_momento_x,
            self.spin_momento_y,
            self.spin_momento_z,
            self.combo_tipo_combinacion,
            self.campo_convencion_signos,
        )
        with señales_bloqueadas(*widgets):
            if instancia is None:
                for spin in (
                    self.spin_axial,
                    self.spin_cortante_x,
                    self.spin_cortante_y,
                    self.spin_momento_x,
                    self.spin_momento_y,
                    self.spin_momento_z,
                ):
                    spin.setValue(0.0)
                self.combo_tipo_combinacion.setCurrentIndex(0)
                self.campo_convencion_signos.setText("")
            else:
                self.spin_axial.setValue(instancia.axial_kn)
                self.spin_cortante_x.setValue(instancia.cortante_x_kn)
                self.spin_cortante_y.setValue(instancia.cortante_y_kn)
                self.spin_momento_x.setValue(instancia.momento_x_knm)
                self.spin_momento_y.setValue(instancia.momento_y_knm)
                self.spin_momento_z.setValue(instancia.momento_z_knm)
                indice = self.combo_tipo_combinacion.findData(instancia.tipo_combinacion)
                self.combo_tipo_combinacion.setCurrentIndex(indice if indice >= 0 else 0)
                self.campo_convencion_signos.setText(instancia.convencion_signos)
        self._ocultar_error()
