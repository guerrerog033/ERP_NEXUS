from aplicacion.comunes.auditoria_documento import (
    auditar_cabecera_antes,
    registrar_auditoria_cabecera,
)
from aplicacion.framework.datagrid.filtros import (
    LookupFilter,
    construir_filtros,
)
from aplicacion.framework.table.registros_model import (
    RegistrosModel,
)
from aplicacion.framework.table.table_definition import (
    TableDefinition,
)
from aplicacion.framework.table.column import (
    Column,
)
from PySide6.QtCore import Qt


class _ServicioPrueba:

    entidad_auditoria = "DocumentoPrueba"

    modulo_auditoria = "prueba"

    @classmethod
    def obtener_por_id(
        cls,
        id_registro,
    ):

        class _Registro:

            total = 100
            estado = "borrador"

        return _Registro()


def test_auditar_cabecera_antes():

    cambios = auditar_cabecera_antes(
        _ServicioPrueba,
        1,
        {
            "total": 200,
            "estado": "borrador",
        },
    )

    assert "total" in cambios


def test_lookup_filter_con_objeto_resultado():

    filtro = LookupFilter(
        "cliente_id",
    )

    consulta = filtro.a_consulta(
        type(
            "R",
            (),
            {
                "valor": 15,
            },
        )(),
    )

    assert consulta is not None

    assert consulta.valor == 15


def test_registros_model_alineacion_decimal():

    definition = TableDefinition(
        columnas=[
            Column(
                "total",
                "Total",
                widget="decimal",
            ),
        ],
    )

    modelo = RegistrosModel(
        definition,
    )

    modelo.establecer_registros(
        [
            {
                "total": 1,
            },
        ],
    )

    indice = modelo.index(
        0,
        0,
    )

    alineacion = modelo.data(
        indice,
        Qt.TextAlignmentRole,
    )

    assert alineacion is not None

    assert int(
        alineacion,
    ) & int(
        Qt.AlignRight,
    )
