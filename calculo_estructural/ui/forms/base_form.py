"""Base común de los formularios de sección y utilidades compartidas.

Cada formulario concreto implementa ``_construir_modelo()`` (reconstruye
su sub-modelo de Pydantic a partir de los widgets actuales) y
``cargar_datos(instancia)`` (puebla los widgets desde una instancia
existente, o los deja en blanco si es ``None``). El banner de error y
cuándo emitir ``datos_aplicados`` viven aquí, para no repetirlos en cada
uno de los 7 formularios.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from pydantic import ValidationError
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QLabel, QLineEdit, QWidget

from ...models import TipoAcero


@contextmanager
def señales_bloqueadas(*widgets: QWidget) -> Iterator[None]:
    """Bloquea temporalmente las señales de todos los ``widgets`` dados.

    Se usa dentro de ``cargar_datos()`` para poblar varios widgets a la
    vez sin disparar el auto-aplicado de cada uno (que reaccionaría a una
    simple recarga como si fuera una edición del usuario).
    """
    for widget in widgets:
        widget.blockSignals(True)
    try:
        yield
    finally:
        for widget in widgets:
            widget.blockSignals(False)


class SeccionFormBase(QWidget):
    """Formulario de una sección del proyecto.

    No se instancia directamente: las subclases implementan
    ``_construir_modelo()`` y ``cargar_datos()``.
    """

    datos_aplicados = Signal(object)
    """Se emite con la nueva instancia del sub-modelo cuando se aplica
    con éxito (después de pasar la validación de Pydantic)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._banner_error = QLabel()
        self._banner_error.setWordWrap(True)
        self._banner_error.setStyleSheet("color: #c53030; background-color: #fdecea; padding: 4px;")
        self._banner_error.hide()

    @property
    def banner_error(self) -> QLabel:
        """El ``QLabel`` de error, para que la subclase lo agregue a su
        propio layout donde le convenga."""
        return self._banner_error

    def _construir_modelo(self) -> Any:
        """Las subclases devuelven ``ModeloX(**valores)`` con los valores
        actuales de los widgets. Puede lanzar ``ValidationError`` (regla
        de Pydantic) o ``ValueError`` (p. ej. una tabla de coordenadas
        con texto no numérico) — ambas se muestran de la misma forma."""
        raise NotImplementedError

    def cargar_datos(self, instancia: Any) -> None:
        """Puebla los widgets desde ``instancia`` (o los deja en su
        estado por defecto si es ``None``). Debe bloquear las señales de
        sus propios widgets mientras lo hace (ver ``señales_bloqueadas``)."""
        raise NotImplementedError

    def _intentar_aplicar(self) -> None:
        """Reconstruye el sub-modelo con los valores actuales; si es
        válido, oculta el banner y emite ``datos_aplicados``; si no,
        muestra el error y no emite nada (el proyecto conserva el último
        valor válido, que puede seguir siendo ``None``)."""
        try:
            instancia = self._construir_modelo()
        except (ValidationError, ValueError) as error:
            self._mostrar_error(error)
            return
        self._ocultar_error()
        self.datos_aplicados.emit(instancia)

    def _mostrar_error(self, error: ValidationError | ValueError) -> None:
        if isinstance(error, ValidationError):
            lineas = [f"• {'.'.join(str(parte) for parte in e['loc'])}: {e['msg']}" for e in error.errors()]
            texto = "Datos inválidos:\n" + "\n".join(lineas)
        else:
            texto = f"Datos inválidos: {error}"
        self._banner_error.setText(texto)
        self._banner_error.show()

    def _ocultar_error(self) -> None:
        self._banner_error.hide()


class CamposMaterial(QWidget):
    """Grupo reutilizable de 3 campos: tipo de acero, Fy (MPa) y el texto
    libre para cuando el tipo de acero es OTRO (se habilita/deshabilita
    solo). Lo comparten ``PlacaBaseForm`` y ``PerfilMetalicoForm`` (las 5
    formas de sección de perfil comparten estos mismos 3 campos)."""

    valores_cambiados = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_tipo_acero = QComboBox()
        for tipo in TipoAcero:
            self.combo_tipo_acero.addItem(tipo.value, tipo)
        self.combo_tipo_acero.currentIndexChanged.connect(self._on_tipo_acero_cambiado)
        self.combo_tipo_acero.currentIndexChanged.connect(lambda _indice: self.valores_cambiados.emit())

        self.campo_tipo_acero_otro = QLineEdit()
        self.campo_tipo_acero_otro.setEnabled(False)
        self.campo_tipo_acero_otro.setPlaceholderText("Designación (obligatorio si el tipo es OTRO)")
        self.campo_tipo_acero_otro.editingFinished.connect(self.valores_cambiados.emit)

        self.spin_fy = QDoubleSpinBox()
        self.spin_fy.setRange(0.01, 5000.0)
        self.spin_fy.setDecimals(1)
        self.spin_fy.setSuffix(" MPa")
        self.spin_fy.setKeyboardTracking(False)
        self.spin_fy.setValue(250.0)
        self.spin_fy.valueChanged.connect(lambda _valor: self.valores_cambiados.emit())

        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addRow("Tipo de acero:", self.combo_tipo_acero)
        layout.addRow("Si es OTRO, especifique:", self.campo_tipo_acero_otro)
        layout.addRow("Fy (MPa):", self.spin_fy)

    def _on_tipo_acero_cambiado(self, _indice: int) -> None:
        self.campo_tipo_acero_otro.setEnabled(self.combo_tipo_acero.currentData() == TipoAcero.OTRO)

    def valores(self) -> dict:
        return dict(
            tipo_acero=self.combo_tipo_acero.currentData(),
            tipo_acero_otro=self.campo_tipo_acero_otro.text().strip() or None,
            fy_mpa=self.spin_fy.value(),
        )

    def cargar(self, tipo_acero: TipoAcero, tipo_acero_otro: str | None, fy_mpa: float) -> None:
        with señales_bloqueadas(self.combo_tipo_acero, self.campo_tipo_acero_otro, self.spin_fy):
            indice = self.combo_tipo_acero.findData(tipo_acero)
            self.combo_tipo_acero.setCurrentIndex(indice if indice >= 0 else 0)
            self.campo_tipo_acero_otro.setText(tipo_acero_otro or "")
            self.campo_tipo_acero_otro.setEnabled(tipo_acero == TipoAcero.OTRO)
            self.spin_fy.setValue(fy_mpa)
