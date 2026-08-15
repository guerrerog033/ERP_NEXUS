from aplicacion.framework.crud.trabajo_listado import TrabajoListado
from aplicacion.framework.datagrid.datagrid import DataGrid
from aplicacion.framework.datagrid.toolbar import MaestroToolbar
from aplicacion.framework.form.modo import (
    ModoFormulario,
    resolver_modo,
)
from aplicacion.framework.ui.loading_overlay import LoadingOverlay


def _qapp():
    from PySide6.QtCore import QThread
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app, QThread


def test_resolver_modo_formulario():
    assert resolver_modo(
        None,
        None,
    ) == ModoFormulario.NUEVO

    assert resolver_modo(
        None,
        5,
    ) == ModoFormulario.EDICION

    assert resolver_modo(
        ModoFormulario.CONSULTA,
        5,
    ) == ModoFormulario.CONSULTA


def test_maestro_toolbar_unificada():
    _qapp()

    toolbar = MaestroToolbar()

    assert toolbar.btn_nuevo.objectName() == "BotonPrimario"
    assert toolbar.btn_consultar.text() == "Consultar"
    assert toolbar.btn_mas.objectName() == "MaestroToolbarMas"
    assert toolbar.txt_buscar.placeholderText() == "Buscar..."


def test_datagrid_expone_toolbar_crud():
    _qapp()

    grid = DataGrid()

    assert grid.btn_nuevo is grid.toolbar.btn_nuevo
    assert grid.btn_consultar is grid.toolbar.btn_consultar
    assert hasattr(
        grid,
        "mostrar_carga",
    )


def test_loading_overlay_mensaje():
    _qapp()

    from PySide6.QtWidgets import QWidget

    contenedor = QWidget()
    contenedor.resize(
        400,
        300,
    )
    contenedor.show()

    overlay = LoadingOverlay(
        contenedor,
    )

    overlay.mostrar(
        "Cargando registros...",
    )

    assert overlay.isVisible()
    assert "Cargando" in overlay.lbl_mensaje.text()

    overlay.ocultar()

    assert not overlay.isVisible()


def test_trabajo_listado_ejecuta_consulta():
    capturado = {}

    def consulta():
        capturado["ok"] = True
        return {"registros": [1, 2]}

    trabajo = TrabajoListado(
        consulta,
    )

    resultados = []

    trabajo.terminado.connect(
        lambda valor: resultados.append(
            valor,
        ),
    )

    trabajo.ejecutar()

    assert capturado.get(
        "ok",
    )
    assert resultados[
        0
    ]["registros"] == [
        1,
        2,
    ]
