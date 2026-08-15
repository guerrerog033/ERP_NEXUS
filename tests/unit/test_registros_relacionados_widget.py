from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QDialog

from aplicacion.maestros.terceros.registros_relacionados_widget import (
    CampoRegistro,
    ListaRegistrosTerceroWidget,
)


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


class _ServicioFalso:
    """
    Doble en memoria del servicio (misma interfaz listar/guardar/
    actualizar/eliminar) para probar el widget sin tocar la BD.
    """

    def __init__(self):
        self._siguiente_id = 1
        self.registros: dict[int, SimpleNamespace] = {}

    def listar(self, tercero_id):
        return [
            r
            for r in self.registros.values()
            if r.tercero_id == tercero_id
        ]

    def guardar(self, datos):
        if not str(datos.get("banco", "")).strip():
            raise ValueError("El campo 'banco' es obligatorio.")

        registro = SimpleNamespace(
            id=self._siguiente_id,
            **datos,
        )
        self.registros[registro.id] = registro
        self._siguiente_id += 1
        return registro

    def actualizar(self, id_registro, datos):
        registro = self.registros[id_registro]
        for campo, valor in datos.items():
            setattr(registro, campo, valor)
        return registro

    def eliminar(self, id_registro):
        self.registros.pop(id_registro, None)


def _columnas():
    return [
        ("banco", "Banco"),
        ("numero_cuenta", "Número"),
        ("principal", "Principal"),
    ]


def _campos():
    return [
        CampoRegistro("banco", "Banco", requerido=True),
        CampoRegistro("numero_cuenta", "Número de cuenta", requerido=True),
        CampoRegistro("principal", "Principal", tipo="bool"),
    ]


def _widget():
    _qapp()

    return ListaRegistrosTerceroWidget(
        servicio=_ServicioFalso(),
        columnas=_columnas(),
        campos=_campos(),
        titulo_dialogo="Cuenta bancaria",
    )


def test_cargar_muestra_los_registros_existentes():
    widget = _widget()

    widget.servicio.guardar(
        {
            "tercero_id": 1,
            "banco": "Bancolombia",
            "numero_cuenta": "111",
        },
    )

    widget.cargar(1)

    assert widget.tabla.rowCount() == 1
    assert widget.tabla.item(0, 0).text() == "Bancolombia"


def test_cargar_sin_tercero_id_deja_tabla_vacia():
    widget = _widget()

    widget.cargar(None)

    assert widget.tabla.rowCount() == 0


def test_agregar_no_hace_nada_sin_tercero_cargado():
    widget = _widget()

    widget._agregar()

    assert widget.tabla.rowCount() == 0


def test_agregar_via_dialogo_guarda_y_refresca():
    widget = _widget()

    widget.cargar(7)

    with patch.object(
        ListaRegistrosTerceroWidget,
        "_agregar",
        wraps=widget._agregar,
    ):
        with patch(
            "aplicacion.maestros.terceros.registros_relacionados_widget.DialogoRegistro",
        ) as MockDialogo:
            instancia = MockDialogo.return_value
            instancia.exec.return_value = QDialog.DialogCode.Accepted
            instancia.valores.return_value = {
                "banco": "Davivienda",
                "numero_cuenta": "999",
                "principal": False,
            }

            widget._agregar()

    assert widget.tabla.rowCount() == 1
    assert widget.tabla.item(0, 0).text() == "Davivienda"
    assert list(widget.servicio.registros.values())[0].tercero_id == 7


def test_agregar_muestra_error_si_falla_validacion():
    widget = _widget()

    widget.cargar(1)

    with patch(
        "aplicacion.maestros.terceros.registros_relacionados_widget.DialogoRegistro",
    ) as MockDialogo, patch(
        "aplicacion.maestros.terceros.registros_relacionados_widget.QMessageBox.warning",
    ) as mock_warning:
        instancia = MockDialogo.return_value
        instancia.exec.return_value = QDialog.DialogCode.Accepted
        instancia.valores.return_value = {
            "banco": "",
            "numero_cuenta": "999",
            "principal": False,
        }

        widget._agregar()

    mock_warning.assert_called_once()
    assert widget.tabla.rowCount() == 0


def test_eliminar_confirma_y_borra():
    widget = _widget()

    registro = widget.servicio.guardar(
        {
            "tercero_id": 3,
            "banco": "Bancolombia",
            "numero_cuenta": "111",
        },
    )

    widget.cargar(3)

    widget.tabla.selectRow(0)

    with patch(
        "aplicacion.maestros.terceros.registros_relacionados_widget.QMessageBox.question",
        return_value=__import__(
            "PySide6.QtWidgets",
            fromlist=["QMessageBox"],
        ).QMessageBox.StandardButton.Yes,
    ):
        widget._eliminar()

    assert widget.tabla.rowCount() == 0
    assert registro.id not in widget.servicio.registros


def test_eliminar_cancelado_no_borra():
    widget = _widget()

    widget.servicio.guardar(
        {
            "tercero_id": 3,
            "banco": "Bancolombia",
            "numero_cuenta": "111",
        },
    )

    widget.cargar(3)

    widget.tabla.selectRow(0)

    from PySide6.QtWidgets import QMessageBox

    with patch(
        "aplicacion.maestros.terceros.registros_relacionados_widget.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No,
    ):
        widget._eliminar()

    assert widget.tabla.rowCount() == 1
