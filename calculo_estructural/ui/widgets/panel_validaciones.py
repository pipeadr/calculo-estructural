"""Tabla que muestra los ``ResultadoValidacion`` del proyecto actual,
coloreada según severidad.

No calcula ninguna regla propia: solo presenta lo que
``validation.validar_proyecto()`` ya calculó (lo llama
``ui.estado_proyecto.EstadoProyecto``, nunca este widget).
"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ...validation import EstadoValidacion, ResultadoValidacion

_COLUMNAS = ("Estado", "Componente(s)", "Código", "Mensaje")

# Fondo claro + texto oscuro fijados explícitamente: con Windows en modo
# oscuro, el texto hereda blanco por defecto y quedaba casi ilegible
# sobre estos fondos claros si no se fija también el color de letra.
_COLOR_TEXTO = QColor("#1a1a1a")

_COLOR_FONDO_POR_ESTADO = {
    EstadoValidacion.OK: QColor("#e6f4ea"),
    EstadoValidacion.ADVERTENCIA: QColor("#fff4e5"),
    EstadoValidacion.ERROR: QColor("#fdecea"),
    EstadoValidacion.NO_VERIFICADO: QColor("#e8e8e8"),
}


class PanelValidaciones(QWidget):
    """Lista de validación cruzada, una fila por ``ResultadoValidacion``."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tabla = QTableWidget(0, len(_COLUMNAS))
        self._tabla.setHorizontalHeaderLabels(_COLUMNAS)
        self._tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._tabla.setSortingEnabled(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabla)

    def actualizar(self, resultados: list[ResultadoValidacion]) -> None:
        """Reemplaza el contenido de la tabla por ``resultados``."""
        self._tabla.setRowCount(len(resultados))
        for fila, resultado in enumerate(resultados):
            valores = (
                resultado.estado.value,
                ", ".join(componente.value for componente in resultado.componentes),
                resultado.codigo,
                resultado.mensaje,
            )
            color_fondo = _COLOR_FONDO_POR_ESTADO[resultado.estado]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                item.setBackground(color_fondo)
                item.setForeground(_COLOR_TEXTO)
                self._tabla.setItem(fila, columna, item)

    def resumen_por_estado(self, resultados: list[ResultadoValidacion]) -> str:
        """Texto corto tipo "0 errores · 2 advertencias" para la barra
        de estado."""
        conteo = {estado: 0 for estado in EstadoValidacion}
        for resultado in resultados:
            conteo[resultado.estado] += 1
        return (
            f"{conteo[EstadoValidacion.ERROR]} error(es) · "
            f"{conteo[EstadoValidacion.ADVERTENCIA]} advertencia(s) · "
            f"{conteo[EstadoValidacion.NO_VERIFICADO]} sin verificar"
        )

    def cantidad_filas(self) -> int:
        return self._tabla.rowCount()

    def texto_de(self, fila: int, columna: int) -> str:
        item = self._tabla.item(fila, columna)
        return item.text() if item is not None else ""
