"""Fixtures compartidas por las pruebas de calculo_estructural.ui.

Qt solo permite una QApplication por proceso — toda la sesión de pytest
comparte una sola instancia. Ninguna prueba llama a `.show()` ni a
`.exec()`: solo se instancian widgets y se leen/escriben sus valores, así
que no hace falta un display real ni un event loop.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
