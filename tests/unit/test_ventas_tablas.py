from __future__ import annotations

from aplicacion.modulos.ventas.cotizaciones.cotizacion_definition import (
    CotizacionDefinition,
)
from aplicacion.modulos.ventas.cotizaciones.cotizaciones_table import (
    CotizacionTable,
)
from aplicacion.modulos.ventas.facturas.factura_definition import (
    FacturaVentaDefinition,
)
from aplicacion.modulos.ventas.facturas.facturas_table import (
    FacturaVentaTable,
)
from aplicacion.modulos.ventas.notas_credito.nota_definition import (
    NotaCreditoVentaDefinition,
)
from aplicacion.modulos.ventas.notas_credito.notas_credito_table import (
    NotaCreditoVentaTable,
)
from aplicacion.modulos.ventas.notas_debito.nota_definition import (
    NotaDebitoVentaDefinition,
)
from aplicacion.modulos.ventas.notas_debito.notas_debito_table import (
    NotaDebitoVentaTable,
)
from aplicacion.modulos.ventas.pedidos.pedido_definition import (
    PedidoDefinition,
)
from aplicacion.modulos.ventas.pedidos.pedidos_table import (
    PedidoTable,
)
from aplicacion.modulos.ventas.remisiones.remision_definition import (
    RemisionDefinition,
)
from aplicacion.modulos.ventas.remisiones.remisiones_table import (
    RemisionTable,
)


def test_definiciones_tabla_ventas():
    assert CotizacionDefinition.table_definition is CotizacionTable
    assert PedidoDefinition.table_definition is PedidoTable
    assert RemisionDefinition.table_definition is RemisionTable
    assert FacturaVentaDefinition.table_definition is FacturaVentaTable
    assert NotaCreditoVentaDefinition.table_definition is NotaCreditoVentaTable
    assert NotaDebitoVentaDefinition.table_definition is NotaDebitoVentaTable
    assert len(
        FacturaVentaTable.columnas,
    ) >= 8
