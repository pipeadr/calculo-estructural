"""Tabla editable de coordenadas (x, y) en mm, reutilizada por el
formulario de placa base (perforaciones) y el de pernos (posiciones).

No conoce ningún modelo de Pydantic: solo trabaja con tuplas ``(x, y)``
— el formulario que la use es quien las convierte en
``Perforacion``/``PosicionPerno`` y quien decide qué hacer si
``obtener_puntos()`` levanta ``ValueError`` por una celda no numérica.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

_COLUMNAS = ("X (mm)", "Y (mm)")


class TablaCoordenadas(QWidget):
    """Tabla de 2 columnas (X, Y) con botones para agregar/quitar filas."""

    puntos_cambiados = Signal()
    """Se emite cuando el usuario agrega, quita o edita un punto (no
    cuando se recarga la tabla vía ``cargar_puntos``)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tabla = QTableWidget(0, len(_COLUMNAS))
        self._tabla.setHorizontalHeaderLabels(_COLUMNAS)
        self._tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tabla.itemChanged.connect(lambda _item: self.puntos_cambiados.emit())

        boton_agregar = QPushButton("Agregar punto")
        boton_agregar.clicked.connect(lambda: self._agregar_fila())
        boton_quitar = QPushButton("Quitar seleccionado(s)")
        boton_quitar.clicked.connect(lambda: self._quitar_filas_seleccionadas())

        botones = QHBoxLayout()
        botones.addWidget(boton_agregar)
        botones.addWidget(boton_quitar)
        botones.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabla)
        layout.addLayout(botones)

    def _agregar_fila(self, x: float = 0.0, y: float = 0.0) -> None:
        # blockSignals evita que los dos setItem() de abajo disparen
        # itemChanged (que también reemite puntos_cambiados) además del
        # emit() explícito al final — sin esto, agregar una fila emitía
        # la señal 3 veces en vez de 1.
        self._tabla.blockSignals(True)
        fila = self._tabla.rowCount()
        self._tabla.insertRow(fila)
        self._tabla.setItem(fila, 0, QTableWidgetItem(f"{x:g}"))
        self._tabla.setItem(fila, 1, QTableWidgetItem(f"{y:g}"))
        self._tabla.blockSignals(False)
        self.puntos_cambiados.emit()

    def _quitar_filas_seleccionadas(self) -> None:
        filas = sorted({indice.row() for indice in self._tabla.selectedIndexes()}, reverse=True)
        if not filas:
            return
        for fila in filas:
            self._tabla.removeRow(fila)
        self.puntos_cambiados.emit()

    def cargar_puntos(self, puntos: list[tuple[float, float]]) -> None:
        """Reemplaza el contenido de la tabla por ``puntos``, sin
        disparar ``puntos_cambiados`` (es una recarga, no una edición del
        usuario)."""
        self._tabla.blockSignals(True)
        self._tabla.setRowCount(0)
        for x, y in puntos:
            fila = self._tabla.rowCount()
            self._tabla.insertRow(fila)
            self._tabla.setItem(fila, 0, QTableWidgetItem(f"{x:g}"))
            self._tabla.setItem(fila, 1, QTableWidgetItem(f"{y:g}"))
        self._tabla.blockSignals(False)

    def obtener_puntos(self) -> list[tuple[float, float]]:
        """Lee la tabla y devuelve los puntos como floats.

        Lanza ``ValueError`` si alguna celda no es un número — el
        formulario que la usa decide cómo mostrarlo (junto con los
        ``ValidationError`` del modelo, ver ``forms.base_form``).
        """
        puntos = []
        for fila in range(self._tabla.rowCount()):
            item_x = self._tabla.item(fila, 0)
            item_y = self._tabla.item(fila, 1)
            x = float(item_x.text()) if item_x and item_x.text().strip() else 0.0
            y = float(item_y.text()) if item_y and item_y.text().strip() else 0.0
            puntos.append((x, y))
        return puntos

    def cantidad(self) -> int:
        return self._tabla.rowCount()
