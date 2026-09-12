"""Interfaz gráfica (PySide6).

No contiene ningún cálculo ni regla de validación propia: usa
``calculo_estructural.models`` para los datos, ``calculo_estructural.validation``
para las reglas cruzadas, ``calculo_estructural.persistencia`` para
guardar/abrir y ``calculo_estructural.dibujo`` para las vistas.
"""

from __future__ import annotations

from .estado_proyecto import EstadoProyecto, GuardadoBloqueadoPorErroresError
from .main_window import MainWindow

__all__ = ["EstadoProyecto", "GuardadoBloqueadoPorErroresError", "MainWindow"]
