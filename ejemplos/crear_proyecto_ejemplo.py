"""Script de prueba manual — Fase 1 (modelos, validaciones y persistencia).

Construye un Proyecto completo a partir de valores que TÚ puedes editar
en la sección "DATOS DE ENTRADA" de este mismo archivo, lo valida con
Pydantic (Etapa 1) y con las validaciones cruzadas entre componentes
(Etapa 2), lo guarda como JSON y lo vuelve a abrir (Etapa 3), y muestra
en consola cada paso. No usa pytest ni la interfaz gráfica (todavía no
existe, llega en la Etapa 6): es la forma más directa de probar el
proyecto completo con tus propios números.

Cómo usarlo
-----------
1. Edita los valores en "DATOS DE ENTRADA" más abajo (dimensiones, tipo de
   acero, coordenadas, cargas, etc.).
2. Ejecuta desde la raíz del repositorio:

       .venv\\Scripts\\python.exe ejemplos\\crear_proyecto_ejemplo.py

3. Revisa la consola: cada sección se marca [OK] o [ERROR] (reglas propias
   de cada modelo, Etapa 1). Si hay [ERROR], el mensaje indica el campo y
   la regla que falló — corrige y vuelve a ejecutar.
4. Después se corren las VALIDACIONES CRUZADAS (Etapa 2): cada regla se
   lista como OK, ERROR, ADVERTENCIA o NO_VERIFICADO con su mensaje. Con
   los valores por defecto ya vas a ver 2 ADVERTENCIA (convención de
   signos y tipo de combinación de carga no definidos) y 1 NO_VERIFICADO
   (espesor máximo de soldadura, pendiente de un criterio normativo).
5. Por último, PERSISTENCIA (Etapa 3): guarda el proyecto en
   ejemplos/proyecto_generado.json con guardar_proyecto(), imprime el
   contenido del archivo, lo vuelve a abrir con cargar_proyecto() y
   confirma que es idéntico al original.

Prueba a romper algo a propósito para ver cómo se reporta:
- `PERNOS["diametro_in"] = 1.25` (mayor que la perforación) -> ERROR en
  PERNO_PERFORACION_DIAMETRO (validación cruzada, no bloquea el guardado).
- Mueve una coordenada de `PERNOS["posiciones"]` lejos de la placa ->
  ERROR en PERNOS_DENTRO_DE_PLACA y PERNO_PERFORACION_CORRESPONDENCIA.
- Duplica una coordenada en `PLACA["perforaciones"]` -> ERROR en
  PERFORACIONES_DUPLICADAS.
- `tipo_acero=TipoAcero.OTRO` sin `tipo_acero_otro` -> [ERROR] a nivel de
  modelo (Etapa 1), antes de llegar a las validaciones cruzadas.
- Edita a mano ejemplos/proyecto_generado.json después de generarlo (por
  ejemplo, borra una coma o cambia `"version_formato": "1.0"` por
  `"9.9"`) y vuelve a correr solo la parte de abrir — ver la sección
  "Cómo probarlo manualmente" en la respuesta del asistente para el
  fragmento de código exacto.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Permite ejecutar este script directamente (python ejemplos/archivo.py)
# sin instalar el paquete ni usar `python -m`: agrega la raíz del
# repositorio (un nivel arriba de ejemplos/) al principio de sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError  # noqa: E402

from calculo_estructural.models import (  # noqa: E402
    Cargas,
    ElementoConcreto,
    MetadatosProyecto,
    Perforacion,
    PerfilCircular,
    PerfilCuadrado,
    PerfilH,
    PerfilI,
    PerfilRectangular,
    Pernos,
    PlacaBase,
    PosicionPerno,
    Proyecto,
    Soldadura,
    TipoAcero,
    TipoElementoConcreto,
    TipoGradoPerno,
    TipoSoldadura,
)
from calculo_estructural.persistencia import ProyectoIOError, cargar_proyecto, guardar_proyecto  # noqa: E402
from calculo_estructural.validation import resumen_por_estado, validar_proyecto  # noqa: E402

# =====================================================================
# DATOS DE ENTRADA — edita libremente estos valores y vuelve a ejecutar
# =====================================================================

NOMBRE_PROYECTO = "Conexion columna HSS 200x200 - Placa base"
AUTOR = "Tu nombre"
DESCRIPCION = "Ejemplo editable de la Fase 1"

# --- Placa base ---
PLACA = dict(
    largo_mm=450,
    ancho_mm=450,
    espesor_mm=25,
    tipo_acero=TipoAcero.A36,
    fy_mpa=250,
    numero_perforaciones=4,
    diametro_perforacion_in=1.0,
    perforaciones=[
        Perforacion(x_mm=170, y_mm=170),
        Perforacion(x_mm=-170, y_mm=170),
        Perforacion(x_mm=-170, y_mm=-170),
        Perforacion(x_mm=170, y_mm=-170),
    ],
)

# --- Perfil metálico ---
# Cambia TIPO_SECCION a "rectangular", "cuadrada", "circular", "I" o "H"
# y ajusta los campos del diccionario correspondiente más abajo.
TIPO_SECCION = "cuadrada"

PERFIL_RECTANGULAR = dict(
    tipo_acero=TipoAcero.A500_GR_B, fy_mpa=317,
    b_mm=200, h_mm=300, es_hueco=True, espesor_pared_mm=8,
)
PERFIL_CUADRADO = dict(
    tipo_acero=TipoAcero.A500_GR_B, fy_mpa=317,
    lado_mm=200, es_hueco=True, espesor_pared_mm=8,
)
PERFIL_CIRCULAR = dict(
    tipo_acero=TipoAcero.A500_GR_C, fy_mpa=317,
    diametro_mm=219.1, es_hueco=True, espesor_pared_mm=6,
)
PERFIL_I = dict(
    tipo_acero=TipoAcero.A992, fy_mpa=345,
    peralte_mm=300, ancho_ala_mm=150, espesor_ala_mm=12, espesor_alma_mm=8,
)
PERFIL_H = dict(
    tipo_acero=TipoAcero.A992, fy_mpa=345,
    peralte_mm=300, ancho_ala_mm=300, espesor_ala_mm=15, espesor_alma_mm=10,
)

# --- Elemento de concreto ---
CONCRETO = dict(
    tipo_elemento=TipoElementoConcreto.PEDESTAL,
    largo_mm=700,
    ancho_mm=700,
    altura_mm=600,
    fc_mpa=28,
)

# --- Pernos de anclaje ---
# diametro_in + 1/8" (holgura estándar, ver validation/configuracion.py)
# debe dar exactamente diametro_perforacion_in de la placa de arriba.
PERNOS = dict(
    cantidad=4,
    diametro_in=0.875,
    longitud_mm=400,
    tipo_grado=TipoGradoPerno.F1554_GR36,
    profundidad_embebido_mm=300,
    posiciones=[
        PosicionPerno(x_mm=170, y_mm=170),
        PosicionPerno(x_mm=-170, y_mm=170),
        PosicionPerno(x_mm=-170, y_mm=-170),
        PosicionPerno(x_mm=170, y_mm=-170),
    ],
)

# --- Soldadura ---
SOLDADURA = dict(
    tipo_soldadura=TipoSoldadura.FILETE,
    simbolo="Filete continuo, ambos lados",
    espesor_mm=8,
    longitud_mm=200,
)

# --- Cargas (kN y kN·m) en la interfaz perfil-placa ---
# Se dejan sin definir tipo_combinacion y convencion_signos a propósito,
# para que el reporte de validaciones más abajo muestre cómo se ven esas
# dos ADVERTENCIA. Para quitarlas, agrega por ejemplo:
#   tipo_combinacion=TipoCombinacionCarga.FACTORIZADA,
#   convencion_signos="Axial positivo = compresión",
# (import TipoCombinacionCarga desde calculo_estructural.models)
CARGAS = dict(
    axial_kn=-180.0,
    cortante_x_kn=25.0,
    cortante_y_kn=-10.0,
    momento_x_knm=8.0,
    momento_y_knm=4.0,
    momento_z_knm=0.0,
)

# =====================================================================
# A partir de aquí no hace falta tocar nada
# =====================================================================

_PERFILES_POR_TIPO = {
    "rectangular": (PerfilRectangular, PERFIL_RECTANGULAR),
    "cuadrada": (PerfilCuadrado, PERFIL_CUADRADO),
    "circular": (PerfilCircular, PERFIL_CIRCULAR),
    "I": (PerfilI, PERFIL_I),
    "H": (PerfilH, PERFIL_H),
}


def _separador(titulo: str) -> None:
    print(f"\n--- {titulo} " + "-" * max(1, 50 - len(titulo)))


def construir_proyecto() -> Proyecto:
    """Construye el Proyecto sección por sección, reportando en consola
    cada una como [OK] o [ERROR] sin detener el script — así se ven de
    una vez todos los problemas, no solo el primero."""
    ahora = datetime.now()
    proyecto = Proyecto(
        metadatos=MetadatosProyecto(
            nombre=NOMBRE_PROYECTO or "Proyecto sin nombre",
            descripcion=DESCRIPCION,
            autor=AUTOR,
            fecha_creacion=ahora,
            fecha_modificacion=ahora,
        )
    )

    clase_perfil, datos_perfil = _PERFILES_POR_TIPO[TIPO_SECCION]
    secciones = {
        "placa_base": (PlacaBase, PLACA),
        "perfil_metalico": (clase_perfil, datos_perfil),
        "elemento_concreto": (ElementoConcreto, CONCRETO),
        "pernos": (Pernos, PERNOS),
        "soldadura": (Soldadura, SOLDADURA),
        "cargas": (Cargas, CARGAS),
    }

    for nombre_campo, (clase, datos) in secciones.items():
        _separador(nombre_campo)
        try:
            instancia = clase(**datos)
        except ValidationError as error:
            print(f"[ERROR] Datos invalidos en '{nombre_campo}':")
            for err in error.errors():
                campo = ".".join(str(parte) for parte in err["loc"])
                print(f"   - {campo}: {err['msg']}")
            continue
        setattr(proyecto, nombre_campo, instancia)
        print(f"[OK] {nombre_campo} configurado correctamente.")

    return proyecto


def mostrar_resumen(proyecto: Proyecto) -> None:
    _separador("RESUMEN")
    for campo in (
        "placa_base", "perfil_metalico", "elemento_concreto",
        "pernos", "soldadura", "cargas",
    ):
        estado = "completa" if getattr(proyecto, campo) is not None else "FALTA / con errores (ver arriba)"
        print(f"  - {campo}: {estado}")


def mostrar_validaciones(proyecto: Proyecto) -> None:
    """Corre las validaciones cruzadas de la Etapa 2 y las imprime.

    Esto es lo que en la Etapa 6 hará el botón "Validar" de la interfaz:
    aquí simplemente se listan los ResultadoValidacion en consola.
    """
    _separador("VALIDACIONES CRUZADAS (Etapa 2)")
    resultados = validar_proyecto(proyecto)
    conteo = resumen_por_estado(resultados)
    print(
        f"  Resumen: {conteo['OK']} OK, {conteo['ERROR']} ERROR, "
        f"{conteo['ADVERTENCIA']} ADVERTENCIA, {conteo['NO_VERIFICADO']} NO_VERIFICADO\n"
    )
    for resultado in resultados:
        print(f"  [{resultado.estado.value:^13}] {resultado.codigo} - {resultado.nombre}")
        print(f"                  {resultado.mensaje}")


def guardar_y_abrir_de_nuevo(proyecto: Proyecto) -> None:
    """Demuestra la Etapa 3: guarda el proyecto en JSON con
    guardar_proyecto(), lo vuelve a leer con cargar_proyecto(), y
    confirma que el resultado es idéntico al original. Esto es lo mismo
    que hará "Guardar"/"Abrir" en la interfaz de la Etapa 6.
    """
    _separador("PERSISTENCIA (Etapa 3)")
    ruta = Path(__file__).resolve().parent / "proyecto_generado.json"

    resultado_guardado = guardar_proyecto(proyecto, ruta)
    print(f"  Guardado en: {ruta}")
    print(f"  Validación al guardar: {resumen_por_estado(resultado_guardado.resultados_validacion)}")

    print(f"\n  Contenido del archivo ({ruta.name}):\n")
    print(ruta.read_text(encoding="utf-8"))

    try:
        resultado_abierto = cargar_proyecto(ruta)
    except ProyectoIOError as error:
        print(f"\n  [ERROR] No se pudo volver a abrir el proyecto: {error}")
        return

    if resultado_abierto.proyecto == proyecto:
        print("\n  [OK] El proyecto reabierto es idéntico al original: no se perdió información.")
    else:
        print("\n  [ERROR] El proyecto reabierto NO coincide con el original.")
    print(f"  Validación al abrir: {resumen_por_estado(resultado_abierto.resultados_validacion)}")


if __name__ == "__main__":
    proyecto = construir_proyecto()
    mostrar_resumen(proyecto)
    mostrar_validaciones(proyecto)
    guardar_y_abrir_de_nuevo(proyecto)
