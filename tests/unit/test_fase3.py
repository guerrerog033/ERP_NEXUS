from unittest.mock import MagicMock

from aplicacion.comunes.transaccion import (
    transaccion_negocio,
)
from aplicacion.nucleo.auditoria_campos import (
    AuditoriaCampos,
)


def test_transaccion_negocio_commit(
    monkeypatch,
):

    sesion = MagicMock()

    monkeypatch.setattr(
        "aplicacion.comunes.transaccion.SessionLocal",
        lambda: sesion,
    )

    with transaccion_negocio():

        pass

    sesion.commit.assert_called_once()
    sesion.close.assert_called_once()


def test_transaccion_negocio_rollback(
    monkeypatch,
):

    sesion = MagicMock()

    monkeypatch.setattr(
        "aplicacion.comunes.transaccion.SessionLocal",
        lambda: sesion,
    )

    try:

        with transaccion_negocio():

            raise ValueError(
                "fallo",
            )

    except ValueError:

        pass

    sesion.rollback.assert_called_once()
    sesion.commit.assert_not_called()
    sesion.close.assert_called_once()


def test_auditoria_campos_detectar_cambios():

    class _Registro:

        razon_social = "Antigua"
        activo = True

    cambios = AuditoriaCampos.detectar_cambios(
        _Registro(),
        {
            "razon_social": "Nueva",
            "activo": True,
        },
    )

    assert list(
        cambios.keys(),
    ) == [
        "razon_social",
    ]

    assert cambios[
        "razon_social"
    ] == (
        "Antigua",
        "Nueva",
    )


def test_tercero_servicio_listar_paginado(
    monkeypatch,
):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    llamadas = {}

    def _consultar(
        **kwargs,
    ):

        llamadas.update(
            kwargs,
        )

        return {
            "registros": [],
            "total": 0,
            "pagina": 1,
            "por_pagina": 50,
        }

    monkeypatch.setattr(
        TerceroServicio.repositorio,
        "consultar",
        _consultar,
    )

    TerceroServicio.listar(
        pagina=2,
        por_pagina=50,
        tipo_tercero="Cliente",
    )

    assert llamadas[
        "pagina"
    ] == 2

    assert llamadas[
        "tipo_tercero"
    ] == "Cliente"


def test_registros_model_filas():

    from aplicacion.framework.table.registros_model import (
        RegistrosModel,
    )

    from aplicacion.framework.table.table_definition import (
        TableDefinition,
    )

    from aplicacion.framework.table.column import (
        Column,
    )

    definition = TableDefinition(
        columnas=[
            Column(
                "id",
                "ID",
            ),
            Column(
                "nombre",
                "Nombre",
            ),
        ],
    )

    modelo = RegistrosModel(
        definition,
    )

    modelo.establecer_registros(
        [
            {
                "id": 1,
                "nombre": "A",
            },
            {
                "id": 2,
                "nombre": "B",
            },
        ],
    )

    assert modelo.rowCount() == 2
    assert modelo.columnCount() == 2
    assert (
        modelo.data(
            modelo.index(
                0,
                1,
            ),
        )
        == "A"
    )
