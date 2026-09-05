"""Tolerancias y criterios usados por las validaciones cruzadas.

Se centralizan aquí, en vez de quedar como números sueltos dentro de cada
regla, para que sea evidente de dónde sale cada uno — cuál es un dato
provisto explícitamente para este proyecto y cuál es solo una tolerancia
numérica de conveniencia — y para poder ajustarlos (o exponerlos como
configuración de usuario) en una fase futura sin tocar la lógica de las
reglas.
"""

from __future__ import annotations

HOLGURA_ESTANDAR_PERFORACION_IN = 0.125
"""Sobre-diámetro estándar entre la perforación de la placa y el perno
que aloja: perforación = diámetro del perno + 1/8". Dato indicado
explícitamente para este proyecto, no una norma asumida por el modelo."""

TOLERANCIA_COORDENADAS_MM = 1.0
"""Distancia (mm) por debajo de la cual dos coordenadas se consideran
"la misma posición", para emparejar perno↔perforación o detectar
duplicados. Es una tolerancia de conveniencia por entrada manual de
datos, no un criterio normativo."""

TOLERANCIA_DIAMETRO_IN = 1e-6
"""Tolerancia numérica (in) para comparar diámetros de punto flotante por
igualdad, evitando falsos positivos de ADVERTENCIA por redondeo."""
