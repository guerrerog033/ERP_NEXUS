from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from aplicacion.framework.datasource.result import DataResult
from aplicacion.maestros.terceros.cliente_lookup import ClienteLookup
from aplicacion.maestros.terceros.proveedor_lookup import ProveedorLookup


def _registro_tercero(
    *,
    id_registro: int,
    tipo_tercero: str,
    razon_social: str = "",
    numero_documento: str = "",
    nombre_completo: str = "",
):
    return SimpleNamespace(
        id=id_registro,
        tipo_tercero=tipo_tercero,
        razon_social=razon_social,
        numero_documento=numero_documento,
        nombre_completo=nombre_completo or razon_social,
    )


def test_cliente_lookup_filtra_solo_clientes():
    datasource = MagicMock()
    datasource.listar.return_value = DataResult(
        registros=[
            _registro_tercero(
                id_registro=1,
                tipo_tercero="Cliente",
                razon_social="Cliente Demo S.A.S.",
                numero_documento="900111222",
            ),
            _registro_tercero(
                id_registro=2,
                tipo_tercero="Proveedor",
                razon_social="Proveedor Demo",
                numero_documento="800333444",
            ),
        ],
    )

    lookup = ClienteLookup()
    lookup.datasource = datasource

    resultados = lookup.buscar(
        "",
    )

    assert len(
        resultados,
    ) == 1
    assert resultados[0].valor == 1
    assert resultados[0].codigo == "900111222"
    assert (
        "Cliente Demo"
        in resultados[0].texto
    )


def test_cliente_lookup_busca_por_documento():
    datasource = MagicMock()
    datasource.listar.return_value = DataResult(
        registros=[
            _registro_tercero(
                id_registro=1,
                tipo_tercero="Cliente",
                razon_social="",
                numero_documento="1234567890",
                nombre_completo="Ana López",
            ),
        ],
    )

    lookup = ClienteLookup()
    lookup.datasource = datasource

    resultados = lookup.buscar(
        "1234",
    )

    assert len(
        resultados,
    ) == 1
    assert resultados[0].texto == "Ana López"


def test_proveedor_lookup_filtra_solo_proveedores():
    datasource = MagicMock()
    datasource.listar.return_value = DataResult(
        registros=[
            _registro_tercero(
                id_registro=1,
                tipo_tercero="Cliente",
                razon_social="Cliente Demo",
                numero_documento="111",
            ),
            _registro_tercero(
                id_registro=2,
                tipo_tercero="Proveedor",
                razon_social="Proveedor Demo S.A.S.",
                numero_documento="900555666",
            ),
        ],
    )

    lookup = ProveedorLookup()
    lookup.datasource = datasource

    resultados = lookup.buscar(
        "",
    )

    assert len(
        resultados,
    ) == 1
    assert resultados[0].valor == 2
    assert resultados[0].codigo == "900555666"


def test_proveedor_lookup_excluye_texto_sin_coincidencia():
    datasource = MagicMock()
    datasource.listar.return_value = DataResult(
        registros=[
            _registro_tercero(
                id_registro=2,
                tipo_tercero="Proveedor",
                razon_social="Proveedor Demo S.A.S.",
                numero_documento="900555666",
            ),
        ],
    )

    lookup = ProveedorLookup()
    lookup.datasource = datasource

    resultados = lookup.buscar(
        "cliente",
    )

    assert resultados == []
