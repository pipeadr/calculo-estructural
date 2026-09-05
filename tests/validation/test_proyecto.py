"""Pruebas del orquestador validar_proyecto sobre el Proyecto completo."""

from __future__ import annotations

from calculo_estructural.models import Proyecto
from calculo_estructural.validation import EstadoValidacion, hay_errores, resumen_por_estado, validar_proyecto

# --- Caso 10: proyecto completamente válido -----------------------------


def test_proyecto_de_ejemplo_no_tiene_errores(proyecto_ejemplo: Proyecto):
    resultados = validar_proyecto(proyecto_ejemplo)
    assert not hay_errores(resultados)

    conteo = resumen_por_estado(resultados)
    assert conteo["ERROR"] == 0
    # El fixture no documenta convención de signos ni tipo de combinación
    # de carga, y el espesor máximo de soldadura queda pendiente a
    # propósito (criterio normativo no definido): se esperan justamente
    # esas advertencias/no-verificado, nada más.
    assert conteo["ADVERTENCIA"] == 2
    assert conteo["NO_VERIFICADO"] == 1


def test_proyecto_vacio_reporta_no_verificado_en_todas_las_categorias(proyecto_ejemplo: Proyecto):
    proyecto_vacio = Proyecto(metadatos=proyecto_ejemplo.metadatos)
    resultados = validar_proyecto(proyecto_vacio)

    assert not hay_errores(resultados)
    conteo = resumen_por_estado(resultados)
    assert conteo["OK"] == 0
    assert conteo["ADVERTENCIA"] == 0
    assert conteo["NO_VERIFICADO"] == len(resultados)


def test_hay_errores_detecta_un_perno_incompatible_con_la_perforacion(proyecto_ejemplo: Proyecto):
    proyecto_con_perno_incompatible = proyecto_ejemplo.model_copy(deep=True)
    proyecto_con_perno_incompatible.pernos = proyecto_con_perno_incompatible.pernos.model_copy(
        update={"diametro_in": 5.0}
    )

    resultados = validar_proyecto(proyecto_con_perno_incompatible)

    assert hay_errores(resultados)
    resultado_diametro = next(r for r in resultados if r.codigo == "PERNO_PERFORACION_DIAMETRO")
    assert resultado_diametro.estado == EstadoValidacion.ERROR
