"""Diálogo para pedir los datos de un proyecto nuevo: nombre
(obligatorio), autor y descripción (opcionales)."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget


class NuevoProyectoDialog(QDialog):
    """Pide nombre/autor/descripción para ``EstadoProyecto.nuevo_proyecto``."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo proyecto")

        self.campo_nombre = QLineEdit()
        self.campo_autor = QLineEdit()
        self.campo_descripcion = QPlainTextEdit()
        self.campo_descripcion.setMaximumHeight(80)

        formulario = QFormLayout()
        formulario.addRow("Nombre:", self.campo_nombre)
        formulario.addRow("Autor:", self.campo_autor)
        formulario.addRow("Descripción:", self.campo_descripcion)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self._intentar_aceptar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botones)

    def _intentar_aceptar(self) -> None:
        if not self.campo_nombre.text().strip():
            self.campo_nombre.setFocus()
            return
        self.accept()

    def valores(self) -> tuple[str, str, str]:
        """(nombre, autor, descripcion), ya recortados de espacios."""
        return (
            self.campo_nombre.text().strip(),
            self.campo_autor.text().strip(),
            self.campo_descripcion.toPlainText().strip(),
        )
