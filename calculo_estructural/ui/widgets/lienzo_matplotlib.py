"""Lienzo genérico para incrustar una ``Figure`` de Matplotlib en un
widget de Qt. Lo reutilizan la vista en planta y la sección transversal
dentro de la ventana principal — ninguna de las dos sabe nada de Qt por
sí misma (``dibujo/`` solo depende de Matplotlib)."""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget


class LienzoMatplotlib(QWidget):
    """Envuelve un ``FigureCanvasQTAgg`` y expone ``mostrar_figura()``
    para reemplazar la figura dibujada sin recrear el widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._canvas = FigureCanvasQTAgg(Figure())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

    @property
    def canvas(self) -> FigureCanvasQTAgg:
        return self._canvas

    def mostrar_figura(self, figura: Figure) -> None:
        """Reemplaza la figura mostrada por ``figura`` y repinta."""
        self._canvas.figure = figura
        figura.set_canvas(self._canvas)
        self._canvas.draw()
