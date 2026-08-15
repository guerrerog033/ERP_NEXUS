from __future__ import annotations

import os
import uuid

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)


pytestmark = pytest.mark.integration


@pytest.fixture(
    scope="session",
    autouse=True,
)
def _registrar_modelos():

    importar_modelos()


@pytest.fixture(
    scope="session",
)
def requiere_postgresql():

    if not os.getenv(
        "DB_HOST",
    ):

        pytest.skip(
            "DB_HOST no configurado",
        )


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@pytest.fixture
def tercero_con_cuenta(
    requiere_postgresql,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioCuentaBancariaTercero,
    )

    sufijo = uuid.uuid4().hex[:8]

    documento = str(
        900000000
        + int(sufijo[:6], 16) % 100000000,
    )

    tercero = TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": documento,
            "tipo_tercero": "Cliente",
            "razon_social": f"Tercero Formulario Demo {sufijo}",
            "direccion": "Calle 1 # 2-3",
            "pais": "Colombia",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "correo": f"formulario.{sufijo}@demo.com",
            "dias_credito": 0,
            "cupo_credito": 0,
            "resp_r99_pn": True,
        },
    )

    ServicioCuentaBancariaTercero.guardar(
        {
            "tercero_id": tercero.id,
            "banco": "Bancolombia",
            "numero_cuenta": "1234567890",
        },
    )

    return tercero


def test_formulario_edicion_muestra_pestanas_de_registros(
    tercero_con_cuenta,
):
    from aplicacion.maestros.terceros.formulario import (
        TerceroFormulario,
    )

    _qapp()

    form = TerceroFormulario(
        id_registro=tercero_con_cuenta.id,
    )

    assert hasattr(
        form,
        "_widgets_registros_relacionados",
    )

    assert len(
        form._widgets_registros_relacionados,
    ) == 3

    widget_cuentas = form._widgets_registros_relacionados[2]

    assert widget_cuentas.tabla.rowCount() == 1
    assert widget_cuentas.tabla.item(0, 0).text() == "Bancolombia"


def test_formulario_nuevo_no_muestra_pestanas_de_registros(
    requiere_postgresql,
):
    from aplicacion.maestros.terceros.formulario import (
        TerceroFormulario,
    )

    _qapp()

    form = TerceroFormulario()

    assert not hasattr(
        form,
        "_widgets_registros_relacionados",
    )


def test_formulario_edicion_permite_generar_acceso_al_portal(
    tercero_con_cuenta,
):
    from aplicacion.maestros.terceros.formulario import (
        TerceroFormulario,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    _qapp()

    form = TerceroFormulario(
        id_registro=tercero_con_cuenta.id,
    )

    from aplicacion.maestros.terceros.portal_acceso_widget import (
        PortalAccesoWidget,
    )

    portal_tab = next(
        (
            widget
            for widget in form.findChildren(
                PortalAccesoWidget,
            )
        ),
        None,
    )

    assert portal_tab is not None
    assert portal_tab.txt_enlace.text() == ""

    portal_tab._generar()

    assert "portal/mi-cuenta/" in portal_tab.txt_enlace.text()

    tercero_actualizado = TerceroServicio.obtener_por_id(
        tercero_con_cuenta.id,
    )

    assert tercero_actualizado.portal_token is not None
    assert (
        tercero_actualizado.portal_token
        in portal_tab.txt_enlace.text()
    )
