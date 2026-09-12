"""Formulario del perfil metálico: un combo de tipo de sección que
cambia entre 5 páginas (una por forma), más los 3 campos de material que
comparten las 5 (``CamposMaterial``, común con ``PlacaBaseForm``).
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QStackedWidget, QVBoxLayout, QWidget

from ...models import (
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilMetalico,
    PerfilRectangular,
    TipoAcero,
    TipoSeccionPerfil,
)
from .base_form import CamposMaterial, SeccionFormBase, señales_bloqueadas

_CLASE_POR_TIPO = {
    TipoSeccionPerfil.RECTANGULAR: PerfilRectangular,
    TipoSeccionPerfil.CUADRADA: PerfilCuadrado,
    TipoSeccionPerfil.CIRCULAR: PerfilCircular,
    TipoSeccionPerfil.I: PerfilI,
    TipoSeccionPerfil.H: PerfilH,
}


def _spin_mm(valor_inicial: float) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.01, 100000.0)
    spin.setDecimals(2)
    spin.setSuffix(" mm")
    spin.setKeyboardTracking(False)
    spin.setValue(valor_inicial)
    return spin


class _PaginaHueca(QWidget):
    """Campos compartidos por rectangular/cuadrado/circular: si el
    perfil es tubular (``es_hueco``) y, si lo es, su espesor de pared."""

    cambiado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.check_hueco = QCheckBox("Es hueco (tubular / HSS)")
        self.check_hueco.toggled.connect(self._on_hueco_toggled)
        self.check_hueco.toggled.connect(lambda _marcado: self.cambiado.emit())

        self.spin_espesor_pared = _spin_mm(6.0)
        self.spin_espesor_pared.setEnabled(False)
        self.spin_espesor_pared.valueChanged.connect(lambda _valor: self.cambiado.emit())

    def _on_hueco_toggled(self, marcado: bool) -> None:
        self.spin_espesor_pared.setEnabled(marcado)

    def valores_hueco(self) -> dict:
        return dict(
            es_hueco=self.check_hueco.isChecked(),
            espesor_pared_mm=self.spin_espesor_pared.value() if self.check_hueco.isChecked() else None,
        )

    def cargar_hueco(self, es_hueco: bool, espesor_pared_mm: float | None) -> None:
        with señales_bloqueadas(self.check_hueco, self.spin_espesor_pared):
            self.check_hueco.setChecked(es_hueco)
            self.spin_espesor_pared.setEnabled(es_hueco)
            self.spin_espesor_pared.setValue(espesor_pared_mm or 6.0)


class _PaginaRectangular(_PaginaHueca):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spin_b = _spin_mm(200.0)
        self.spin_h = _spin_mm(300.0)
        self.spin_b.valueChanged.connect(lambda _valor: self.cambiado.emit())
        self.spin_h.valueChanged.connect(lambda _valor: self.cambiado.emit())

        formulario = QFormLayout(self)
        formulario.addRow("Ancho b (mm):", self.spin_b)
        formulario.addRow("Altura h (mm):", self.spin_h)
        formulario.addRow(self.check_hueco)
        formulario.addRow("Espesor de pared (mm):", self.spin_espesor_pared)

    def valores(self) -> dict:
        return dict(b_mm=self.spin_b.value(), h_mm=self.spin_h.value(), **self.valores_hueco())

    def cargar(self, perfil: PerfilRectangular) -> None:
        with señales_bloqueadas(self.spin_b, self.spin_h):
            self.spin_b.setValue(perfil.b_mm)
            self.spin_h.setValue(perfil.h_mm)
        self.cargar_hueco(perfil.es_hueco, perfil.espesor_pared_mm)


class _PaginaCuadrado(_PaginaHueca):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spin_lado = _spin_mm(200.0)
        self.spin_lado.valueChanged.connect(lambda _valor: self.cambiado.emit())

        formulario = QFormLayout(self)
        formulario.addRow("Lado (mm):", self.spin_lado)
        formulario.addRow(self.check_hueco)
        formulario.addRow("Espesor de pared (mm):", self.spin_espesor_pared)

    def valores(self) -> dict:
        return dict(lado_mm=self.spin_lado.value(), **self.valores_hueco())

    def cargar(self, perfil: PerfilCuadrado) -> None:
        with señales_bloqueadas(self.spin_lado):
            self.spin_lado.setValue(perfil.lado_mm)
        self.cargar_hueco(perfil.es_hueco, perfil.espesor_pared_mm)


class _PaginaCircular(_PaginaHueca):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spin_diametro = _spin_mm(200.0)
        self.spin_diametro.valueChanged.connect(lambda _valor: self.cambiado.emit())

        formulario = QFormLayout(self)
        formulario.addRow("Diámetro (mm):", self.spin_diametro)
        formulario.addRow(self.check_hueco)
        formulario.addRow("Espesor de pared (mm):", self.spin_espesor_pared)

    def valores(self) -> dict:
        return dict(diametro_mm=self.spin_diametro.value(), **self.valores_hueco())

    def cargar(self, perfil: PerfilCircular) -> None:
        with señales_bloqueadas(self.spin_diametro):
            self.spin_diametro.setValue(perfil.diametro_mm)
        self.cargar_hueco(perfil.es_hueco, perfil.espesor_pared_mm)


class _PaginaIH(QWidget):
    """Página compartida por I y H: los mismos 4 parámetros geométricos."""

    cambiado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spin_peralte = _spin_mm(300.0)
        self.spin_ancho_ala = _spin_mm(150.0)
        self.spin_espesor_ala = _spin_mm(12.0)
        self.spin_espesor_alma = _spin_mm(8.0)
        for spin in (self.spin_peralte, self.spin_ancho_ala, self.spin_espesor_ala, self.spin_espesor_alma):
            spin.valueChanged.connect(lambda _valor: self.cambiado.emit())

        formulario = QFormLayout(self)
        formulario.addRow("Peralte d (mm):", self.spin_peralte)
        formulario.addRow("Ancho de ala bf (mm):", self.spin_ancho_ala)
        formulario.addRow("Espesor de ala tf (mm):", self.spin_espesor_ala)
        formulario.addRow("Espesor de alma tw (mm):", self.spin_espesor_alma)

    def valores(self) -> dict:
        return dict(
            peralte_mm=self.spin_peralte.value(),
            ancho_ala_mm=self.spin_ancho_ala.value(),
            espesor_ala_mm=self.spin_espesor_ala.value(),
            espesor_alma_mm=self.spin_espesor_alma.value(),
        )

    def cargar(self, perfil: PerfilI | PerfilH) -> None:
        with señales_bloqueadas(self.spin_peralte, self.spin_ancho_ala, self.spin_espesor_ala, self.spin_espesor_alma):
            self.spin_peralte.setValue(perfil.peralte_mm)
            self.spin_ancho_ala.setValue(perfil.ancho_ala_mm)
            self.spin_espesor_ala.setValue(perfil.espesor_ala_mm)
            self.spin_espesor_alma.setValue(perfil.espesor_alma_mm)


class PerfilMetalicoForm(SeccionFormBase):
    """Formulario de ``PerfilMetalico`` (unión discriminada)."""

    _ORDEN_TIPOS = (
        TipoSeccionPerfil.RECTANGULAR,
        TipoSeccionPerfil.CUADRADA,
        TipoSeccionPerfil.CIRCULAR,
        TipoSeccionPerfil.I,
        TipoSeccionPerfil.H,
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_tipo_seccion = QComboBox()
        for tipo in self._ORDEN_TIPOS:
            self.combo_tipo_seccion.addItem(tipo.value, tipo)
        self.combo_tipo_seccion.currentIndexChanged.connect(self._on_tipo_seccion_cambiado)

        self.campos_material = CamposMaterial()
        self.campos_material.valores_cambiados.connect(self._intentar_aplicar)

        self.pagina_rectangular = _PaginaRectangular()
        self.pagina_cuadrado = _PaginaCuadrado()
        self.pagina_circular = _PaginaCircular()
        self.pagina_i = _PaginaIH()
        self.pagina_h = _PaginaIH()
        self._paginas_por_tipo = {
            TipoSeccionPerfil.RECTANGULAR: self.pagina_rectangular,
            TipoSeccionPerfil.CUADRADA: self.pagina_cuadrado,
            TipoSeccionPerfil.CIRCULAR: self.pagina_circular,
            TipoSeccionPerfil.I: self.pagina_i,
            TipoSeccionPerfil.H: self.pagina_h,
        }

        self.paginas = QStackedWidget()
        for tipo in self._ORDEN_TIPOS:
            pagina = self._paginas_por_tipo[tipo]
            pagina.cambiado.connect(self._intentar_aplicar)
            self.paginas.addWidget(pagina)

        formulario_tipo = QFormLayout()
        formulario_tipo.addRow("Tipo de sección:", self.combo_tipo_seccion)

        layout = QVBoxLayout(self)
        layout.addWidget(self.banner_error)
        layout.addLayout(formulario_tipo)
        layout.addWidget(self.campos_material)
        layout.addWidget(self.paginas)
        layout.addStretch(1)

    def _on_tipo_seccion_cambiado(self, indice: int) -> None:
        self.paginas.setCurrentIndex(indice)
        self._intentar_aplicar()

    def _construir_modelo(self) -> PerfilMetalico:
        tipo = self.combo_tipo_seccion.currentData()
        clase = _CLASE_POR_TIPO[tipo]
        pagina = self._paginas_por_tipo[tipo]
        return clase(tipo_seccion=tipo, **self.campos_material.valores(), **pagina.valores())

    def cargar_datos(self, instancia: PerfilMetalico | None) -> None:
        with señales_bloqueadas(self.combo_tipo_seccion):
            if instancia is None:
                self.combo_tipo_seccion.setCurrentIndex(0)
                self.paginas.setCurrentIndex(0)
                self.campos_material.cargar(TipoAcero.A992, None, 250.0)
            else:
                indice = self._ORDEN_TIPOS.index(instancia.tipo_seccion)
                self.combo_tipo_seccion.setCurrentIndex(indice)
                self.paginas.setCurrentIndex(indice)
                self.campos_material.cargar(instancia.tipo_acero, instancia.tipo_acero_otro, instancia.fy_mpa)
                self._paginas_por_tipo[instancia.tipo_seccion].cargar(instancia)
        self._ocultar_error()
