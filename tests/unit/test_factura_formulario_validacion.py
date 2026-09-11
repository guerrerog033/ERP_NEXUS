from __future__ import annotations

from types import SimpleNamespace

from aplicacion.modulos.ventas.cotizaciones.formulario import (
    FormularioCotizacion,
)

_LV = FormularioCotizacion._linea_vacia
_VALIDAR = FormularioCotizacion._validar_documento_basico


def _linea(**kw):
    base = {
        "producto_id": None,
        "descripcion": "",
        "cantidad": 0,
        "precio_unitario": 0,
    }
    base.update(kw)
    return base


def _form_fake():
    return SimpleNamespace(
        cliente=SimpleNamespace(txt=SimpleNamespace()),
        tabla=SimpleNamespace(),
    )


class TestLineaVacia:

    def test_fila_sin_datos_es_vacia(self):
        assert _LV(_linea()) is True

    def test_fila_con_producto_no_es_vacia(self):
        assert _LV(_linea(producto_id=5)) is False

    def test_fila_con_solo_descripcion_no_es_vacia(self):
        assert _LV(_linea(descripcion="Servicio")) is False

    def test_fila_con_solo_cantidad_no_es_vacia(self):
        assert _LV(_linea(cantidad=2)) is False


class TestLineasNoVacias:

    def test_filtra_las_vacias(self):
        form = _form_fake()
        lineas = [
            _linea(producto_id=1, cantidad=1, precio_unitario=1000),
            _linea(),
            _linea(descripcion="Otro", cantidad=3, precio_unitario=500),
        ]
        resultado = FormularioCotizacion._lineas_no_vacias(form, lineas)
        assert len(resultado) == 2


class TestValidarDocumentoBasico:

    def test_sin_cliente_pide_cliente(self):
        form = _form_fake()
        mensaje, foco = _VALIDAR(
            form,
            {"cliente_id": None},
            [_linea(producto_id=1, cantidad=1)],
        )
        assert "cliente" in mensaje.lower()
        assert foco is form.cliente.txt

    def test_sin_lineas_pide_item(self):
        form = _form_fake()
        mensaje, foco = _VALIDAR(form, {"cliente_id": 7}, [])
        assert "ítem" in mensaje.lower() or "item" in mensaje.lower()
        assert foco is form.tabla

    def test_item_sin_producto_ni_descripcion(self):
        form = _form_fake()
        mensaje, _foco = _VALIDAR(
            form,
            {"cliente_id": 7},
            [_linea(cantidad=1, precio_unitario=100)],
        )
        assert "producto ni descripción" in mensaje

    def test_item_con_cantidad_cero(self):
        form = _form_fake()
        mensaje, _foco = _VALIDAR(
            form,
            {"cliente_id": 7},
            [_linea(producto_id=1, cantidad=0, precio_unitario=100)],
        )
        assert "cantidad mayor que cero" in mensaje

    def test_item_con_precio_negativo(self):
        form = _form_fake()
        mensaje, _foco = _VALIDAR(
            form,
            {"cliente_id": 7},
            [_linea(producto_id=1, cantidad=1, precio_unitario=-50)],
        )
        assert "precio negativo" in mensaje

    def test_documento_valido_no_devuelve_mensaje(self):
        form = _form_fake()
        mensaje, foco = _VALIDAR(
            form,
            {"cliente_id": 7},
            [_linea(producto_id=1, cantidad=2, precio_unitario=1500)],
        )
        assert mensaje is None
        assert foco is None
