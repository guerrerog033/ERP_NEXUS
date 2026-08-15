from __future__ import annotations

from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioNotaCreditoCompra
from .servicios import ServicioNotaCreditoCompra


class IntegracionNotaCreditoCompra:

    @classmethod
    def aplicar(
        cls,
        id_registro: int,
    ):

        nota = ServicioNotaCreditoCompra.obtener_completa(
            id_registro,
        )

        if nota is None:

            raise ValueError(
                "No se encontró la nota crédito.",
            )

        if nota.estado == "aplicada":

            raise ValueError(
                "La nota crédito ya fue aplicada.",
            )

        ServicioContabilidad.inicializar_plan()
        ServicioInventario.inicializar_bodega()

        movimientos = (
            ServicioInventario.registrar_salida_nota_credito_compra(
                nota,
            )
        )

        asiento = ServicioContabilidad.registrar_nota_credito_compra(
            nota,
        )

        RepositorioNotaCreditoCompra.reducir_saldo_factura_compra(
            nota.factura_compra_id,
            float(
                nota.total or 0,
            ),
        )

        RepositorioNotaCreditoCompra.actualizar_aplicacion(
            id_registro,
            asiento_id=asiento.id,
            inventario_aplicado=bool(
                movimientos,
            ),
        )

        return asiento

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        return cls.aplicar(
            id_registro,
        )
