from aplicacion.modulos.ventas.comunes.formulario_documento import (
    FormularioDocumentoVenta,
)
from aplicacion.modulos.ventas.pedidos.datasource import (
    PedidoDataSource,
)
from aplicacion.modulos.ventas.pedidos.servicios import (
    ServicioPedido,
)


class FormularioPedido(
    FormularioDocumentoVenta,
):

    titulo = "Pedido"

    servicio_generador = ServicioPedido

    datasource_cls = PedidoDataSource

    mensaje_guardado = "Pedido guardado correctamente."
