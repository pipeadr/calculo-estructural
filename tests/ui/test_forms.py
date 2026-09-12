"""Pruebas de los formularios de sección: cargar_datos() puebla los
widgets, y _construir_modelo() reconstruye el mismo sub-modelo."""

from __future__ import annotations

from calculo_estructural.models import PerfilI, TipoAcero, TipoSeccionPerfil
from calculo_estructural.ui.forms import (
    CargasForm,
    DatosGeneralesForm,
    ElementoConcretoForm,
    PerfilMetalicoForm,
    PernosForm,
    PlacaBaseForm,
    SoldaduraForm,
)

# --- DatosGeneralesForm ---------------------------------------------------


def test_datos_generales_form_cargar_y_reconstruir(qapp, proyecto_ejemplo):
    form = DatosGeneralesForm()

    form.cargar_datos(proyecto_ejemplo.metadatos)
    reconstruido = form._construir_modelo()

    assert reconstruido.nombre == proyecto_ejemplo.metadatos.nombre
    assert reconstruido.autor == proyecto_ejemplo.metadatos.autor
    assert reconstruido.descripcion == proyecto_ejemplo.metadatos.descripcion
    assert reconstruido.fecha_creacion == proyecto_ejemplo.metadatos.fecha_creacion


def test_datos_generales_form_nombre_vacio_muestra_error(qapp, proyecto_ejemplo):
    form = DatosGeneralesForm()
    form.cargar_datos(proyecto_ejemplo.metadatos)

    form.campo_nombre.setText("")
    form.campo_nombre.editingFinished.emit()

    # isVisible() exige que toda la cadena de padres esté mostrada en
    # pantalla (no aplica en una prueba que nunca llama a .show()) —
    # isHidden() sí refleja el estado explícito que controla el formulario.
    assert not form.banner_error.isHidden()


# --- PlacaBaseForm ---------------------------------------------------------


def test_placa_base_form_cargar_y_reconstruir(qapp, placa_base_ejemplo):
    form = PlacaBaseForm()

    form.cargar_datos(placa_base_ejemplo)
    reconstruido = form._construir_modelo()

    assert reconstruido == placa_base_ejemplo


def test_placa_base_form_con_none_deja_valores_por_defecto_sin_error(qapp):
    form = PlacaBaseForm()
    form.cargar_datos(None)

    instancia = form._construir_modelo()

    assert instancia.numero_perforaciones == 0
    assert not form.banner_error.isVisible()


def test_placa_base_form_cantidad_se_deriva_de_la_tabla(qapp, placa_base_ejemplo):
    form = PlacaBaseForm()
    form.cargar_datos(placa_base_ejemplo)

    assert form.tabla_perforaciones.cantidad() == len(placa_base_ejemplo.perforaciones)
    assert str(len(placa_base_ejemplo.perforaciones)) in form.etiqueta_cantidad.text()


def test_placa_base_form_muestra_error_si_tipo_acero_otro_esta_vacio(qapp):
    form = PlacaBaseForm()
    form.cargar_datos(None)

    indice_otro = form.campos_material.combo_tipo_acero.findData(TipoAcero.OTRO)
    form.campos_material.combo_tipo_acero.setCurrentIndex(indice_otro)

    # isVisible() exige que toda la cadena de padres esté mostrada en
    # pantalla (no aplica en una prueba que nunca llama a .show()) —
    # isHidden() sí refleja el estado explícito que controla el formulario.
    assert not form.banner_error.isHidden()


# --- PerfilMetalicoForm -----------------------------------------------------


def test_perfil_metalico_form_cargar_y_reconstruir_rectangular(qapp, perfil_metalico_ejemplo):
    form = PerfilMetalicoForm()

    form.cargar_datos(perfil_metalico_ejemplo)
    reconstruido = form._construir_modelo()

    assert reconstruido == perfil_metalico_ejemplo


def test_perfil_metalico_form_cambiar_tipo_seccion_cambia_de_pagina(qapp):
    form = PerfilMetalicoForm()
    form.cargar_datos(None)

    indice_circular = form.combo_tipo_seccion.findData(TipoSeccionPerfil.CIRCULAR)
    form.combo_tipo_seccion.setCurrentIndex(indice_circular)

    assert form.paginas.currentWidget() is form.pagina_circular
    instancia = form._construir_modelo()
    assert instancia.tipo_seccion == TipoSeccionPerfil.CIRCULAR


def test_perfil_metalico_form_construye_perfil_i(qapp):
    form = PerfilMetalicoForm()
    perfil = PerfilI(
        tipo_acero=TipoAcero.A992, fy_mpa=345,
        peralte_mm=300, ancho_ala_mm=150, espesor_ala_mm=12, espesor_alma_mm=8,
    )

    form.cargar_datos(perfil)
    reconstruido = form._construir_modelo()

    assert reconstruido == perfil
    assert form.paginas.currentWidget() is form.pagina_i


# --- ElementoConcretoForm ---------------------------------------------------


def test_elemento_concreto_form_cargar_y_reconstruir(qapp, elemento_concreto_ejemplo):
    form = ElementoConcretoForm()

    form.cargar_datos(elemento_concreto_ejemplo)
    reconstruido = form._construir_modelo()

    assert reconstruido == elemento_concreto_ejemplo


# --- PernosForm --------------------------------------------------------------


def test_pernos_form_cargar_y_reconstruir(qapp, pernos_ejemplo):
    form = PernosForm()

    form.cargar_datos(pernos_ejemplo)
    reconstruido = form._construir_modelo()

    assert reconstruido == pernos_ejemplo


def test_pernos_form_cantidad_se_deriva_de_la_tabla(qapp, pernos_ejemplo):
    form = PernosForm()
    form.cargar_datos(pernos_ejemplo)

    assert form.tabla_posiciones.cantidad() == pernos_ejemplo.cantidad
    assert str(pernos_ejemplo.cantidad) in form.etiqueta_cantidad.text()


# --- SoldaduraForm -------------------------------------------------------------


def test_soldadura_form_cargar_y_reconstruir(qapp, soldadura_ejemplo):
    form = SoldaduraForm()

    form.cargar_datos(soldadura_ejemplo)
    reconstruido = form._construir_modelo()

    assert reconstruido == soldadura_ejemplo


# --- CargasForm ----------------------------------------------------------------


def test_cargas_form_cargar_y_reconstruir(qapp, cargas_ejemplo):
    form = CargasForm()

    form.cargar_datos(cargas_ejemplo)
    reconstruido = form._construir_modelo()

    assert reconstruido == cargas_ejemplo


def test_cargas_form_admite_valores_negativos(qapp):
    form = CargasForm()
    form.cargar_datos(None)

    form.spin_axial.setValue(-180.0)

    instancia = form._construir_modelo()
    assert instancia.axial_kn == -180.0


# --- Señal datos_aplicados compartida por todos los formularios ------------


def test_form_emite_datos_aplicados_al_editar_un_campo(qapp, cargas_ejemplo):
    form = CargasForm()
    form.cargar_datos(cargas_ejemplo)
    emitidos = []
    form.datos_aplicados.connect(emitidos.append)

    form.spin_axial.setValue(-999.0)

    assert len(emitidos) == 1
    assert emitidos[0].axial_kn == -999.0
