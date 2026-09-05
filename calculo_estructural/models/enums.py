"""Catálogos (listas cerradas de opciones) usados por los modelos del dominio.

Todos incluyen un valor ``OTRO`` para permitir designaciones no listadas;
cuando se elige ``OTRO`` el modelo que lo use exige un campo de texto libre
adicional (ver los ``model_validator`` en cada módulo de ``models``).

Importante: estos catálogos son solo etiquetas descriptivas. En ningún
caso se derivan automáticamente propiedades numéricas (Fy, f'c, etc.) a
partir de la opción elegida — esos valores siempre se ingresan
explícitamente en su propio campo.
"""

from __future__ import annotations

from enum import Enum


class TipoSeccionPerfil(str, Enum):
    """Forma de la sección transversal del perfil metálico."""

    RECTANGULAR = "rectangular"
    CUADRADA = "cuadrada"
    CIRCULAR = "circular"
    I = "I"
    H = "H"


class TipoAcero(str, Enum):
    """Designaciones habituales de acero estructural para perfiles y placas."""

    A36 = "A36"
    A572_GR50 = "A572_GR50"
    A992 = "A992"
    A500_GR_B = "A500_GR_B"
    A500_GR_C = "A500_GR_C"
    OTRO = "OTRO"


class TipoGradoPerno(str, Enum):
    """Designaciones habituales de pernos de anclaje / conexión."""

    A307 = "A307"
    F1554_GR36 = "F1554_GR36"
    F1554_GR55 = "F1554_GR55"
    F1554_GR105 = "F1554_GR105"
    A325 = "A325"
    A490 = "A490"
    OTRO = "OTRO"


class TipoSoldadura(str, Enum):
    """Tipo de junta soldada."""

    FILETE = "filete"
    RANURA_PENETRACION_COMPLETA = "ranura_penetracion_completa"
    RANURA_PENETRACION_PARCIAL = "ranura_penetracion_parcial"
    TAPON = "tapon"
    OTRO = "OTRO"


class TipoElementoConcreto(str, Enum):
    """Tipo de elemento de concreto que recibe la placa base."""

    ZAPATA_AISLADA = "zapata_aislada"
    ZAPATA_COMBINADA = "zapata_combinada"
    PEDESTAL = "pedestal"
    MURO = "muro"
    LOSA = "losa"
    OTRO = "OTRO"


class TipoCombinacionCarga(str, Enum):
    """Si un juego de cargas es factorizado (resistencia última / LRFD) o
    admisible (servicio / ASD). No mezclar ambos sin indicarlo es uno de
    los requisitos de validación de la Etapa 2."""

    FACTORIZADA = "factorizada"
    ADMISIBLE = "admisible"
    NO_ESPECIFICADA = "no_especificada"
