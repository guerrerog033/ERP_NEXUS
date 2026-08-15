from aplicacion.base_datos.tipos import COORDENADA
from aplicacion.comunes.auditoria_documento import (
    auditar_documento_antes,
    auditar_lineas_antes,
)
from aplicacion.comunes.exportacion import (
    _filas_desde_registros,
)
from aplicacion.framework.table.column_factories.status_factory import (
    StatusColumnFactory,
)
from aplicacion.framework.table.registros_model import (
    BadgeRole,
    RegistrosModel,
)
from aplicacion.framework.table.status_column import (
    StatusColumn,
)
from aplicacion.framework.table.table_definition import (
    TableDefinition,
)


class _ServicioLineas:

    entidad_auditoria = "DocumentoLineas"

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        class _Detalle:

            producto_id = 1
            cantidad = 2
            precio_unitario = 10
            total_linea = 20

        class _Doc:

            detalles = [
                _Detalle(),
            ]

        return _Doc()


def test_coordenada_numeric_precision():

    assert str(
        COORDENADA,
    ).endswith(
        "10, 7)",
    )


def test_status_badge_info():

    factory = StatusColumnFactory()

    columna = StatusColumn(
        nombre="estado",
        etiqueta="Estado",
    )

    badge = factory.badge_info(
        "borrador",
        columna,
    )

    assert badge is not None
    assert badge["texto"] == "Borrador"
    assert badge["fondo"] == "#FEF3C7"


def test_registros_model_badge_role():

    definition = TableDefinition(
        columnas=[
            StatusColumn(
                nombre="estado",
                etiqueta="Estado",
            ),
        ],
    )

    modelo = RegistrosModel(
        definition,
    )

    modelo.establecer_registros(
        [
            {
                "estado": "emitida",
            },
        ],
    )

    indice = modelo.index(
        0,
        0,
    )

    badge = modelo.data(
        indice,
        BadgeRole,
    )

    assert badge["texto"] == "Emitida"


def test_auditar_lineas_antes_detecta_cambio():

    cambios = auditar_lineas_antes(
        _ServicioLineas,
        1,
        [
            {
                "producto_id": 1,
                "cantidad": 5,
                "precio_unitario": 10,
                "total_linea": 50,
            },
        ],
    )

    assert "linea[0].cantidad" in cambios


def test_auditar_documento_antes_incluye_lineas():

    class _ServicioDoc(
        _ServicioLineas,
    ):

        @classmethod
        def obtener_por_id(
            cls,
            id_registro,
        ):

            class _Registro:

                total = 100
                estado = "borrador"

            return _Registro()

    cambios = auditar_documento_antes(
        _ServicioDoc,
        1,
        {
            "total": 100,
            "estado": "borrador",
        },
        [
            {
                "producto_id": 1,
                "cantidad": 5,
                "precio_unitario": 10,
                "total_linea": 50,
            },
        ],
    )

    assert "linea[0].cantidad" in cambios


def test_exportacion_filas_desde_registros():

    definition = TableDefinition(
        columnas=[
            StatusColumn(
                nombre="estado",
                etiqueta="Estado",
            ),
        ],
    )

    encabezados, filas = _filas_desde_registros(
        definition,
        [
            {
                "estado": "aprobada",
            },
        ],
    )

    assert encabezados == [
        "Estado",
    ]
    assert filas[0][0] == "Aprobada"
