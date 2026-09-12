"""Formulario de datos generales del proyecto: nombre, autor,
descripción (los campos de ``MetadatosProyecto``).

No es una de las 6 secciones de entrada estructural que pediste, pero sin
él nombre/autor/descripción solo se podrían fijar una vez, al crear el
proyecto, y nunca editar después.
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QFormLayout, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget

from ...models import MetadatosProyecto
from .base_form import SeccionFormBase, señales_bloqueadas


class DatosGeneralesForm(SeccionFormBase):
    """Formulario de ``MetadatosProyecto``. ``fecha_creacion`` y
    ``fecha_modificacion`` se preservan tal cual del proyecto cargado —
    este formulario no las modifica automáticamente."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fecha_creacion: datetime | None = None
        self._fecha_modificacion: datetime | None = None

        self.campo_nombre = QLineEdit()
        self.campo_nombre.editingFinished.connect(self._intentar_aplicar)

        self.campo_autor = QLineEdit()
        self.campo_autor.editingFinished.connect(self._intentar_aplicar)

        self.campo_descripcion = QPlainTextEdit()
        self.campo_descripcion.setMaximumHeight(80)
        self.campo_descripcion.textChanged.connect(self._intentar_aplicar)

        formulario = QFormLayout()
        formulario.addRow("Nombre:", self.campo_nombre)
        formulario.addRow("Autor:", self.campo_autor)
        formulario.addRow("Descripción:", self.campo_descripcion)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(self.banner_error)
        layout.addStretch(1)

    def _construir_modelo(self) -> MetadatosProyecto:
        ahora = datetime.now()
        return MetadatosProyecto(
            nombre=self.campo_nombre.text(),
            autor=self.campo_autor.text(),
            descripcion=self.campo_descripcion.toPlainText(),
            fecha_creacion=self._fecha_creacion or ahora,
            fecha_modificacion=self._fecha_modificacion or ahora,
        )

    def cargar_datos(self, instancia: MetadatosProyecto) -> None:
        self._fecha_creacion = instancia.fecha_creacion
        self._fecha_modificacion = instancia.fecha_modificacion
        with señales_bloqueadas(self.campo_nombre, self.campo_autor, self.campo_descripcion):
            self.campo_nombre.setText(instancia.nombre)
            self.campo_autor.setText(instancia.autor)
            self.campo_descripcion.setPlainText(instancia.descripcion)
        self._ocultar_error()
