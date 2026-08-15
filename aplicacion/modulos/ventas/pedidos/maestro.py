from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.ventas.pedidos.datasource import (
    PedidoDataSource,
)
from aplicacion.modulos.ventas.pedidos.formulario import (
    FormularioPedido,
)
from aplicacion.modulos.ventas.pedidos.pedido_definition import (
    PedidoDefinition,
)
from aplicacion.modulos.ventas.pedidos.vista_pedido import (
    VistaPedido,
)


class FormularioPedidoLista:

    definition = PedidoDefinition


class MaestroPedidos(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Pedidos"

    titulo_singular = "Pedido"

    datasource = PedidoDataSource

    formulario = FormularioPedidoLista

    vista_documento = VistaPedido

    def crear_formulario(
        self,
        id_registro=None,
        parent=None,
        *,
        modo=None,
    ):

        kwargs = {
            "id_registro": id_registro,
        }

        if parent is not None:

            kwargs["parent"] = parent

        return FormularioPedido(
            **kwargs,
        )

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        pedido = self.datasource.obtener_completa(
            id_registro,
        )

        if pedido is None:

            return "Pedido"

        return f"Pedido {pedido.numero}"

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
    ) -> str:

        if id_registro is not None:

            return "Editar Pedido"

        return "Nuevo Pedido"

    def _tamanio_dialogo_formulario(
        self,
        formulario,
    ) -> tuple[int, int]:

        margen = self._margen_dialogo_formulario()

        ancho = min(
            formulario.ancho,
            max(
                1100,
                self.width() - margen,
            ),
        )

        alto = min(
            formulario.alto,
            max(
                520,
                self.height() - margen,
            ),
        )

        return ancho, alto
