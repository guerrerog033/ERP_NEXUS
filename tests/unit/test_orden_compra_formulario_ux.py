from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

pytestmark = pytest.mark.usefixtures(
    "qapp",
)


class _ResultadoFalso:
    def __init__(self, id_: int, codigo: str, texto: str):
        self.id = id_
        self.codigo = codigo
        self.texto = texto


@pytest.fixture
def dialogo(qtbot, monkeypatch):
    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    from aplicacion.modulos.compras.ordenes import vista

    guardados = []

    monkeypatch.setattr(
        vista.ServicioOrdenCompra,
        "guardar",
        lambda **kwargs: guardados.append(kwargs),
    )

    d = vista._DialogoOrdenCompra()
    d.guardados = guardados
    qtbot.addWidget(d)
    d.show()
    qtbot.waitExposed(d)

    return d


def _agregar(d, monkeypatch, id_, cantidad, costo):
    monkeypatch.setattr(
        type(d.producto),
        "producto_id",
        property(lambda self: getattr(self, "_pid_test", None)),
    )
    monkeypatch.setattr(
        type(d.producto),
        "producto_variante_id",
        property(lambda self: None),
    )
    monkeypatch.setattr(
        type(d.producto),
        "resultado",
        property(lambda self: getattr(self, "_res_test", None)),
    )
    monkeypatch.setattr(
        type(d.producto),
        "establecer",
        lambda self, r: (
            setattr(self, "_pid_test", r.id if r else None),
            setattr(self, "_res_test", r),
        ),
    )

    d.producto.establecer(
        _ResultadoFalso(id_, f"P{id_}", f"Producto {id_}"),
    )
    d.cantidad.setValue(cantidad)
    d.costo.setValue(costo)
    d._agregar_linea()


def test_enter_en_cantidad_no_guarda_y_avanza_a_costo(
    dialogo,
    qtbot,
    monkeypatch,
):
    from aplicacion.modulos.compras.ordenes import vista

    # Orden ya guardable: si Enter disparara Guardar, se guardaría.
    _agregar(dialogo, monkeypatch, 1, 1, 10)
    monkeypatch.setattr(dialogo.proveedor, "valor", lambda: 7)
    avisos = []
    monkeypatch.setattr(
        vista.QMessageBox,
        "warning",
        lambda *a, **k: avisos.append(a),
    )

    editor = dialogo.cantidad.lineEdit()
    editor.setFocus()
    qtbot.waitUntil(lambda: editor.hasFocus())

    qtbot.keyClick(
        editor,
        Qt.Key.Key_Return,
    )

    qtbot.waitUntil(
        lambda: dialogo.focusWidget()
        in (dialogo.costo, dialogo.costo.lineEdit()),
    )

    assert dialogo.guardados == []
    assert avisos == []
    assert dialogo.isVisible()


def test_enter_en_costo_agrega_la_linea(dialogo, qtbot, monkeypatch):
    _agregar(dialogo, monkeypatch, 1, 1, 10)
    dialogo.producto.establecer(_ResultadoFalso(2, "P2", "Producto 2"))
    dialogo.costo.setValue(5)

    editor = dialogo.costo.lineEdit()
    editor.setFocus()
    qtbot.waitUntil(lambda: editor.hasFocus())

    qtbot.keyClick(
        editor,
        Qt.Key.Key_Return,
    )

    assert [linea["producto_id"] for linea in dialogo._lineas] == [1, 2]
    assert dialogo.guardados == []


def test_foco_inicial_va_al_selector_de_proveedor(dialogo, qtbot):
    qtbot.waitUntil(
        lambda: dialogo.focusWidget() is dialogo.proveedor.btn,
    )


def test_tabla_es_solo_lectura(dialogo):
    from PySide6.QtWidgets import QAbstractItemView

    assert (
        dialogo.tabla.editTriggers()
        == QAbstractItemView.EditTrigger.NoEditTriggers
    )


def test_quitar_linea_actualiza_lineas_y_total(dialogo, monkeypatch):
    _agregar(dialogo, monkeypatch, 1, 2, 100)
    _agregar(dialogo, monkeypatch, 2, 1, 50)

    assert "250.00" in dialogo.lbl_total.text()

    dialogo.tabla.selectRow(0)
    dialogo._quitar_linea()

    assert [linea["producto_id"] for linea in dialogo._lineas] == [2]
    assert dialogo.tabla.rowCount() == 1
    assert "50.00" in dialogo.lbl_total.text()


def test_guardar_sin_lineas_no_llama_al_servicio(dialogo, monkeypatch):
    from aplicacion.modulos.compras.ordenes import vista

    monkeypatch.setattr(dialogo.proveedor, "valor", lambda: 7)
    monkeypatch.setattr(
        vista.QMessageBox,
        "warning",
        lambda *a, **k: None,
    )

    dialogo._guardar()

    assert dialogo.guardados == []


def test_guardar_con_producto_sin_agregar_no_llama_al_servicio(
    dialogo,
    monkeypatch,
):
    from aplicacion.modulos.compras.ordenes import vista

    _agregar(dialogo, monkeypatch, 1, 1, 10)
    dialogo.producto.establecer(_ResultadoFalso(2, "P2", "Producto 2"))

    monkeypatch.setattr(dialogo.proveedor, "valor", lambda: 7)
    avisos = []
    monkeypatch.setattr(
        vista.QMessageBox,
        "warning",
        lambda *a, **k: avisos.append(a),
    )

    dialogo._guardar()

    assert dialogo.guardados == []
    assert avisos


def test_guardar_valido_envia_las_lineas(dialogo, monkeypatch):
    _agregar(dialogo, monkeypatch, 1, 3, 10)
    dialogo.producto.establecer(None)

    monkeypatch.setattr(dialogo.proveedor, "valor", lambda: 7)

    dialogo._guardar()

    assert len(dialogo.guardados) == 1
    assert dialogo.guardados[0]["proveedor_id"] == 7
    assert dialogo.guardados[0]["lineas"][0]["cantidad"] == 3
