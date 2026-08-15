from aplicacion.modulos.contabilidad.reglas.servicio_reglas import (
    ServicioReglasContabilizacion,
)
from aplicacion.modulos.compras.facturas.emparejador_productos import (
    EmparejadorProductosFactura,
)
from aplicacion.modulos.nomina.exportadores.pila_formato import (
    tarifa_pila,
)
from aplicacion.modulos.tesoreria.conciliacion.servicios import (
    ServicioConciliacionBancaria,
)


def test_tarifa_pila_formato():
    assert tarifa_pila(0.12) == "0120000"
    assert tarifa_pila(0.085) == "0085000"


def test_reglas_contabilizacion_defecto():
    cuentas = (
        ServicioReglasContabilizacion
        .resolver_cuentas_compra(
            producto_tipo="mercancia",
            tiene_producto=True,
        )
    )

    assert cuentas["debito"] == "143501"

    cuentas_gasto = (
        ServicioReglasContabilizacion
        .resolver_cuentas_compra(
            producto_tipo="servicio",
            tiene_producto=True,
        )
    )

    assert cuentas_gasto["debito"] == "613501"


def test_conciliacion_parseo_valor():
    assert (
        ServicioConciliacionBancaria._parsear_valor(
            "$1,250.50",
        )
        == 1250.50
    )


def test_emparejador_sin_codigo():
    producto_id, variante_id = (
        EmparejadorProductosFactura.emparejar_linea(
            descripcion="",
        )
    )

    assert producto_id is None
    assert variante_id is None
