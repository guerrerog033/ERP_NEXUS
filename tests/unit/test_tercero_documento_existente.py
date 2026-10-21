"""
Manejo del documento repetido en el formulario de terceros.

Antes: salir del campo "Número documento" volvía a consultar (local +
DIAN/RUES) aunque no hubiera cambiado; editando un tercero recargaba el
registro y borraba lo editado; creando uno nuevo con un documento ya
registrado copiaba los datos en un registro nuevo que luego fallaba al
guardar con "Ya existe un tercero con ese documento".
"""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from aplicacion.dominio.documentos.resultado import DocumentoResult
from aplicacion.maestros.terceros.formulario import TerceroFormulario


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@contextmanager
def _patch_retenciones():
    with patch(
        "aplicacion.maestros.impuestos.servicios.ServicioImpuesto.inicializar_predeterminados",
    ), patch(
        "aplicacion.maestros.impuestos.retenciones_catalogo.opciones_retencion_combo",
        return_value=[],
    ):
        yield


def _tercero(id_=5, **extra):
    datos = {
        "id": id_,
        "tipo_documento": "CC",
        "numero_documento": "1234567890",
        "dv": "",
        "tipo_tercero": "Cliente",
        "primer_nombre": "Ana",
        "primer_apellido": "López",
        "nombre_completo": "Ana López",
        "pais": "Colombia",
        "activo": True,
    }
    datos.update(extra)
    return SimpleNamespace(**datos)


def _resultado_existente(tercero):
    resultado = DocumentoResult(
        tipo="CC",
        numero="1234567890",
    )
    resultado.existe = True
    resultado.tercero = tercero
    return resultado


def _digitar(form, numero="1234567890", tipo="CC"):
    form.formulario.set_valor("tipo_documento", tipo)
    form.formulario.set_valor("numero_documento", numero)


@_patch_retenciones()
def test_no_repite_consulta_si_documento_no_cambia():
    _qapp()

    form = TerceroFormulario()

    resultado = DocumentoResult(
        tipo="CC",
        numero="1234567890",
        primer_nombre="María",
        primer_apellido="Gómez",
    )

    consulta = MagicMock(return_value=resultado)

    with patch.object(
        form.datasource,
        "documento_changed",
        consulta,
    ), patch.object(
        TerceroFormulario,
        "mostrar_info",
    ), patch.object(
        TerceroFormulario,
        "mostrar_error",
    ):
        _digitar(form)

        form._documento_changed()
        form._documento_changed()

        assert consulta.call_count == 1

        _digitar(form, numero="9876543210")

        form._documento_changed()

        assert consulta.call_count == 2


@_patch_retenciones()
def test_nuevo_con_documento_existente_ofrece_abrirlo_y_pasa_a_edicion():
    _qapp()

    form = TerceroFormulario()

    existente = _tercero()

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=_resultado_existente(existente),
    ), patch.object(
        form.datasource,
        "obtener_por_id",
        return_value=existente,
    ), patch.object(
        TerceroFormulario,
        "_preguntar",
        return_value=True,
    ) as preguntar, patch.object(
        TerceroFormulario,
        "_agregar_registros_relacionados",
    ):
        _digitar(form)

        form._documento_changed()

    preguntar.assert_called_once()
    assert form.es_edicion is True
    assert form.id_registro == 5
    assert form.formulario.binding.valor("primer_nombre") == "Ana"


@_patch_retenciones()
def test_nuevo_con_documento_existente_si_rechaza_sigue_como_nuevo():
    _qapp()

    form = TerceroFormulario()

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=_resultado_existente(_tercero()),
    ), patch.object(
        TerceroFormulario,
        "_preguntar",
        return_value=False,
    ):
        _digitar(form)

        form._documento_changed()

    assert form.es_edicion is False
    assert form.id_registro is None


@_patch_retenciones()
def test_edicion_del_mismo_tercero_no_recarga_ni_avisa():
    _qapp()

    existente = _tercero()

    with patch(
        "aplicacion.maestros.terceros.datasource.TerceroDataSource.obtener_por_id",
        return_value=existente,
    ), patch.object(
        TerceroFormulario,
        "_agregar_registros_relacionados",
    ):
        form = TerceroFormulario(id_registro=5)

    form.formulario.set_valor("primer_nombre", "Editado")

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=_resultado_existente(existente),
    ), patch.object(
        TerceroFormulario,
        "mostrar_info",
    ) as info, patch.object(
        TerceroFormulario,
        "mostrar_error",
    ) as error:
        # Cambia el número y lo devuelve al original: fuerza la
        # consulta y el resultado es el mismo tercero en edición.
        form._ultima_consulta = None

        form._documento_changed()

    info.assert_not_called()
    error.assert_not_called()
    assert form.formulario.binding.valor("primer_nombre") == "Editado"


@_patch_retenciones()
def test_edicion_con_documento_de_otro_tercero_avisa():
    _qapp()

    with patch(
        "aplicacion.maestros.terceros.datasource.TerceroDataSource.obtener_por_id",
        return_value=_tercero(),
    ), patch.object(
        TerceroFormulario,
        "_agregar_registros_relacionados",
    ):
        form = TerceroFormulario(id_registro=5)

    otro = _tercero(
        id_=9,
        numero_documento="555",
        nombre_completo="Pedro Pérez",
    )

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=_resultado_existente(otro),
    ), patch.object(
        TerceroFormulario,
        "mostrar_error",
    ) as error:
        _digitar(form, numero="555")

        form._documento_changed()

    error.assert_called_once()
    assert "Pedro Pérez" in error.call_args.args[0]
    assert form.id_registro == 5


@_patch_retenciones()
def test_edicion_borrar_numero_no_vacia_datos_del_tercero():
    _qapp()

    with patch(
        "aplicacion.maestros.terceros.datasource.TerceroDataSource.obtener_por_id",
        return_value=_tercero(),
    ), patch.object(
        TerceroFormulario,
        "_agregar_registros_relacionados",
    ):
        form = TerceroFormulario(id_registro=5)

    form.formulario.set_valor("numero_documento", "")

    form._documento_changed()

    assert form.formulario.binding.valor("primer_nombre") == "Ana"
