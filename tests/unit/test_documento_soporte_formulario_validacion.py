from __future__ import annotations

from types import SimpleNamespace

from aplicacion.modulos.compras.documentos_soporte.formulario import (
    FormularioDocumentoSoporte,
)

_LV = FormularioDocumentoSoporte._linea_vacia
_VALIDAR = FormularioDocumentoSoporte._validar_documento_basico


def _linea(**kw):
    base = {
        "descripcion": "",
        "cantidad": 0,
        "precio_unitario": 0,
    }
    base.update(kw)
    return base


def _form_fake():
    return SimpleNamespace(
        proveedor=SimpleNamespace(btn=SimpleNamespace()),
        tabla=SimpleNamespace(),
    )


class TestLineaVacia:

    def test_fila_sin_datos_es_vacia(self):
        assert _LV(_linea()) is True

    def test_fila_con_solo_descripcion_no_es_vacia(self):
        assert _LV(_linea(descripcion="Servicio")) is False

    def test_fila_con_solo_cantidad_no_es_vacia(self):
        assert _LV(_linea(cantidad=2)) is False

    def test_fila_con_solo_precio_no_es_vacia(self):
        assert _LV(_linea(precio_unitario=100)) is False


class TestLineasNoVacias:

    def test_filtra_las_vacias(self):
        form = _form_fake()
        lineas = [
            _linea(descripcion="Servicio", cantidad=1, precio_unitario=1000),
            _linea(),
            _linea(descripcion="Otro", cantidad=3, precio_unitario=500),
        ]
        resultado = FormularioDocumentoSoporte._lineas_no_vacias(
            form,
            lineas,
        )
        assert len(resultado) == 2


class TestValidarDocumentoBasico:

    def test_sin_proveedor_pide_proveedor(self):
        form = _form_fake()
        mensaje, foco = _VALIDAR(
            form,
            {"proveedor_id": None},
            [_linea(descripcion="Servicio", cantidad=1)],
        )
        assert "proveedor" in mensaje.lower()
        assert foco is form.proveedor.btn

    def test_sin_lineas_pide_item(self):
        form = _form_fake()
        mensaje, foco = _VALIDAR(form, {"proveedor_id": 7}, [])
        assert "ítem" in mensaje.lower() or "item" in mensaje.lower()
        assert foco is form.tabla

    def test_item_sin_descripcion(self):
        form = _form_fake()
        mensaje, _foco = _VALIDAR(
            form,
            {"proveedor_id": 7},
            [_linea(cantidad=1, precio_unitario=100)],
        )
        assert "no tiene descripción" in mensaje

    def test_item_con_cantidad_cero(self):
        form = _form_fake()
        mensaje, _foco = _VALIDAR(
            form,
            {"proveedor_id": 7},
            [_linea(descripcion="Servicio", cantidad=0, precio_unitario=100)],
        )
        assert "cantidad mayor que cero" in mensaje

    def test_item_con_precio_negativo(self):
        form = _form_fake()
        mensaje, _foco = _VALIDAR(
            form,
            {"proveedor_id": 7},
            [_linea(descripcion="Servicio", cantidad=1, precio_unitario=-50)],
        )
        assert "precio negativo" in mensaje

    def test_documento_valido_no_devuelve_mensaje(self):
        form = _form_fake()
        mensaje, foco = _VALIDAR(
            form,
            {"proveedor_id": 7},
            [_linea(descripcion="Servicio", cantidad=2, precio_unitario=1500)],
        )
        assert mensaje is None
        assert foco is None
