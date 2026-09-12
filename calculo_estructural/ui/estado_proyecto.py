"""Estado y lógica de la aplicación.

``EstadoProyecto`` guarda el ``Proyecto`` actualmente abierto, su ruta en
disco (si ya se guardó/abrió alguna vez) y si tiene cambios sin guardar,
y expone las operaciones de nuevo/abrir/guardar/actualizar una sección.

Es el único lugar de la capa de interfaz que llama a
``calculo_estructural.persistencia`` y ``calculo_estructural.validation``
— los widgets (formularios, ventana principal) nunca lo hacen
directamente, solo reaccionan a la señal ``proyecto_cambiado``. Esto es
lo que permite probar "nuevo/guardar/abrir" sin instanciar ninguna
ventana.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from ..models import MetadatosProyecto, Proyecto
from ..persistencia import ProyectoValidado, cargar_proyecto, guardar_proyecto
from ..validation import EstadoValidacion, ResultadoValidacion, validar_proyecto

NOMBRES_SECCION: tuple[str, ...] = (
    "placa_base",
    "perfil_metalico",
    "elemento_concreto",
    "pernos",
    "soldadura",
    "cargas",
)
"""Nombres de campo de ``Proyecto`` que corresponden a las seis secciones
de datos de entrada editables desde un formulario (no incluye
``metadatos`` ni ``configuracion``, que se editan aparte)."""


class GuardadoBloqueadoPorErroresError(Exception):
    """Se intentó guardar un proyecto con resultados de validación
    cruzada en estado ``ERROR``.

    Esta política ("guardar solo proyectos válidos") vive aquí, en la
    interfaz — no en ``persistencia.guardar_proyecto``, que nunca bloquea
    el guardado (Etapa 3, para poder guardar avances incompletos). Un
    proyecto recién creado no cae en este caso: todas sus secciones
    vacías se reportan como ``NO_VERIFICADO``, no como ``ERROR``.
    """

    def __init__(self, resultados_bloqueantes: list[ResultadoValidacion]) -> None:
        self.resultados_bloqueantes = resultados_bloqueantes
        detalles = "; ".join(f"{r.codigo}: {r.mensaje}" for r in resultados_bloqueantes)
        super().__init__(
            f"No se puede guardar: hay {len(resultados_bloqueantes)} error(es) sin corregir. {detalles}"
        )


class EstadoProyecto(QObject):
    """Contenedor del ``Proyecto`` actualmente abierto y las operaciones
    sobre él. No crea ni conoce ningún widget."""

    proyecto_cambiado = Signal()
    """Se emite cuando cambia el Proyecto completo (nuevo/abierto) o
    cualquiera de sus secciones o metadatos."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._proyecto: Proyecto = self._proyecto_en_blanco("Proyecto sin título")
        self._ruta_actual: Path | None = None
        self._modificado: bool = False

    # --- lectura de estado --------------------------------------------

    @property
    def proyecto(self) -> Proyecto:
        return self._proyecto

    @property
    def ruta_actual(self) -> Path | None:
        return self._ruta_actual

    @property
    def modificado(self) -> bool:
        return self._modificado

    def resultados_validacion(self) -> list[ResultadoValidacion]:
        """Corre ``validation.validar_proyecto()`` sobre el proyecto
        actual. Se recalcula cada vez (no se cachea): las reglas son
        rápidas y así nunca queda desactualizado."""
        return validar_proyecto(self._proyecto)

    # --- operaciones ----------------------------------------------------

    @staticmethod
    def _proyecto_en_blanco(nombre: str, autor: str = "", descripcion: str = "") -> Proyecto:
        ahora = datetime.now()
        return Proyecto(
            metadatos=MetadatosProyecto(
                nombre=nombre,
                autor=autor,
                descripcion=descripcion,
                fecha_creacion=ahora,
                fecha_modificacion=ahora,
            )
        )

    def nuevo_proyecto(self, nombre: str, autor: str = "", descripcion: str = "") -> None:
        """Reemplaza el proyecto actual por uno en blanco (las seis
        secciones en ``None``)."""
        self._proyecto = self._proyecto_en_blanco(nombre, autor, descripcion)
        self._ruta_actual = None
        self._modificado = False
        self.proyecto_cambiado.emit()

    def actualizar_seccion(self, nombre_campo: str, instancia: object) -> None:
        """Reemplaza una sección del proyecto actual (p. ej.
        ``"placa_base"``) por ``instancia``, ya construida y validada por
        su propio modelo Pydantic (esta función no valida nada por su
        cuenta: ``setattr`` sobre ``Proyecto`` revalida solo que el tipo
        encaje, gracias a ``validate_assignment``)."""
        setattr(self._proyecto, nombre_campo, instancia)
        self._modificado = True
        self.proyecto_cambiado.emit()

    def actualizar_metadatos(self, metadatos: MetadatosProyecto) -> None:
        """Reemplaza los metadatos (nombre/autor/descripción) del
        proyecto actual."""
        self._proyecto.metadatos = metadatos
        self._modificado = True
        self.proyecto_cambiado.emit()

    def _resultados_bloqueantes(self) -> list[ResultadoValidacion]:
        return [r for r in self.resultados_validacion() if r.estado == EstadoValidacion.ERROR]

    def guardar(self) -> ProyectoValidado:
        """Guarda en ``ruta_actual``.

        Lanza ``ValueError`` si el proyecto todavía no tiene una ruta
        asignada (usar ``guardar_como`` la primera vez), o
        ``GuardadoBloqueadoPorErroresError`` si hay resultados de
        validación cruzada en ``ERROR``.
        """
        if self._ruta_actual is None:
            raise ValueError("El proyecto no tiene una ruta asignada todavía; usa guardar_como().")
        return self.guardar_como(self._ruta_actual)

    def guardar_como(self, ruta: Path) -> ProyectoValidado:
        """Guarda en ``ruta`` y la recuerda como ``ruta_actual``. Misma
        política de bloqueo por errores que ``guardar``."""
        bloqueantes = self._resultados_bloqueantes()
        if bloqueantes:
            raise GuardadoBloqueadoPorErroresError(bloqueantes)

        resultado = guardar_proyecto(self._proyecto, ruta)
        self._ruta_actual = Path(ruta)
        self._modificado = False
        return resultado

    def abrir(self, ruta: Path) -> ProyectoValidado:
        """Abre un proyecto desde ``ruta`` y lo hace el actual.

        Propaga tal cual cualquier ``ProyectoIOError`` (archivo
        inexistente, JSON inválido, versión no soportada, datos
        inválidos) — no bloquea nada aquí, solo al guardar.
        """
        resultado = cargar_proyecto(ruta)
        self._proyecto = resultado.proyecto
        self._ruta_actual = Path(ruta)
        self._modificado = False
        self.proyecto_cambiado.emit()
        return resultado
