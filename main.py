"""Punto de entrada de la aplicación de escritorio.

Fase 1: modelos de datos, validaciones, persistencia JSON, dibujo
esquemático e interfaz gráfica. No incluye todavía fórmulas de
resistencia normativa (NSR-10 ni ninguna otra).

Ejecutar con:

    .venv\\Scripts\\python.exe main.py
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from calculo_estructural.ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
