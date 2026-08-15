from aplicacion.comunes.auditoria_documento import (
    CAMPOS_LINEA_DEFAULT,
    auditar_lineas_antes,
)
from aplicacion.comunes.exportacion import (
    _filas_desde_registros,
)
from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.framework.table.status_column import (
    StatusColumn,
)
from aplicacion.framework.table.table_definition import (
    TableDefinition,
)


class _ServicioAuditPersonalizado:

    entidad_auditoria = "DocCustom"

    auditoria_campos_linea = [
        "producto_id",
        "cantidad",
        "precio_unitario",
    ]

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
            descripcion = "Item"

        class _Doc:

            detalles = [
                _Detalle(),
            ]

        return _Doc()


def test_servicio_base_auditoria_campos_linea_default():

    assert ServicioBase.auditoria_campos_linea is None


def test_auditar_lineas_respeta_campos_servicio():

    cambios = auditar_lineas_antes(
        _ServicioAuditPersonalizado,
        1,
        [
            {
                "producto_id": 1,
                "cantidad": 5,
                "precio_unitario": 10,
                "total_linea": 50,
                "descripcion": "Item",
            },
        ],
    )

    assert "linea[0].cantidad" in cambios
    assert not any(
        clave.endswith(
            ".total_linea",
        )
        for clave in cambios
    )


def test_auditar_lineas_default_incluye_total_linea():

    class _ServicioDefault(
        _ServicioAuditPersonalizado,
    ):

        auditoria_campos_linea = None

    cambios = auditar_lineas_antes(
        _ServicioDefault,
        1,
        [
            {
                "producto_id": 1,
                "cantidad": 2,
                "precio_unitario": 10,
                "total_linea": 99,
            },
        ],
        campos=CAMPOS_LINEA_DEFAULT,
    )

    assert "linea[0].total_linea" in cambios


def test_exportacion_filas_status_column():

    definition = TableDefinition(
        columnas=[
            StatusColumn(
                nombre="estado_pago",
                etiqueta="Pago",
            ),
        ],
    )

    encabezados, filas = _filas_desde_registros(
        definition,
        [
            {
                "estado_pago": "pagada",
            },
        ],
    )

    assert encabezados == [
        "Pago",
    ]
    assert filas[0][0] == "Pagada"


def test_pos_metodos_pago_esperados():

    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
    )

    app = QApplication.instance()

    if app is None:

        app = QApplication([])

    combo = QComboBox()
    combo.addItem(
        "Efectivo",
        "efectivo",
    )
    combo.addItem(
        "Tarjeta",
        "tarjeta",
    )
    combo.addItem(
        "Transferencia",
        "transferencia",
    )

    metodos = [
        combo.itemData(
            indice,
        )
        for indice in range(
            combo.count(),
        )
    ]

    assert metodos == [
        "efectivo",
        "tarjeta",
        "transferencia",
    ]
