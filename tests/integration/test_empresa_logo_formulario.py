from __future__ import annotations

import os
import uuid
from unittest.mock import patch

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)

pytestmark = pytest.mark.integration


PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452"
    "00000001000000010802000000907753"
    "de0000000c49444154789c63f8cfc000"
    "0003010100c9fe92ef0000000049454e"
    "44ae426082"
)


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


@pytest.fixture(autouse=True)
def _ruta_logos_temporal(
    requiere_postgresql,
    tmp_path,
    monkeypatch,
):

    from aplicacion.maestros.empresas import servicios

    monkeypatch.setattr(
        servicios,
        "RUTA_LOGOS",
        tmp_path / "empresa",
    )


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def _png_archivo(tmp_path) -> str:

    archivo = tmp_path / "logo_prueba.png"

    archivo.write_bytes(
        PNG_1X1,
    )

    return str(archivo)


def _nit_unico() -> str:

    sufijo = uuid.uuid4().hex[:9]

    return str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )


def test_guardar_empresa_nueva_con_logo_persiste_ruta(
    tmp_path,
):
    from aplicacion.maestros.empresas.formulario import (
        EmpresaFormulario,
    )
    from aplicacion.maestros.empresas.repositorio import (
        EmpresaRepositorio,
    )
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    _qapp()

    nit = _nit_unico()

    form = EmpresaFormulario()

    form.widget("nit").setText(nit)
    form.widget("razon_social").setText(
        f"Empresa Logo Demo {nit}",
    )

    archivo = _png_archivo(tmp_path)

    form.logo_widget.establecer_archivo(
        archivo,
    )

    with patch(
        "aplicacion.framework.base.formulario_base.QMessageBox.information",
    ):

        form.guardar()

    empresa = EmpresaRepositorio.obtener_por_nit(
        nit,
    )

    assert empresa is not None
    assert empresa.logo_ruta == f"empresa/{nit}.png"

    ruta_absoluta = EmpresaServicio.ruta_logo_absoluta(
        empresa.logo_ruta,
    )

    assert ruta_absoluta is not None
    assert ruta_absoluta.is_file()


def test_formulario_edicion_precarga_logo_existente(
    tmp_path,
):
    from aplicacion.maestros.empresas.formulario import (
        EmpresaFormulario,
    )
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    _qapp()

    nit = _nit_unico()

    empresa = EmpresaServicio.guardar(
        {
            "razon_social": f"Empresa Con Logo {nit}",
            "nit": nit,
            "pais": "Colombia",
            "activo": True,
            "_logo_archivo": _png_archivo(
                tmp_path,
            ),
        },
    )

    form = EmpresaFormulario(
        id_registro=empresa.id,
    )

    assert form.logo_widget.ruta_relativa() == (
        f"empresa/{nit}.png"
    )
    assert not form.logo_widget.preview.pixmap().isNull()


def test_formulario_edicion_sin_logo_muestra_placeholder(
    requiere_postgresql,
):
    from aplicacion.maestros.empresas.formulario import (
        EmpresaFormulario,
    )
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    _qapp()

    nit = _nit_unico()

    empresa = EmpresaServicio.guardar(
        {
            "razon_social": f"Empresa Sin Logo {nit}",
            "nit": nit,
            "pais": "Colombia",
            "activo": True,
        },
    )

    form = EmpresaFormulario(
        id_registro=empresa.id,
    )

    assert form.logo_widget.ruta_relativa() is None
    assert form.logo_widget.preview.text() == "Sin logo"
