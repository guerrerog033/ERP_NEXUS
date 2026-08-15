from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)

from aplicacion.nucleo.documentos.trazabilidad import (
    vincular_cotizacion_pedido,
)

from .repositorio import RepositorioPedido


class ServicioPedido(ServicioBase):

    repositorio = RepositorioPedido

    entidad_auditoria = "OrdenPedido"

    modulo_auditoria = "ventas/pedidos"

    PREFIJO = "PED"

    LONGITUD = 6

    @classmethod
    def generar_numero(cls) -> str:

        secuencia = cls.repositorio.siguiente_secuencia(
            cls.PREFIJO,
        )

        return (
            f"{cls.PREFIJO}"
            f"{secuencia:0{cls.LONGITUD}d}"
        )

    @classmethod
    def crear_desde_cotizacion(
        cls,
        cotizacion_id: int,
    ):

        existente = cls.repositorio.obtener_por_cotizacion(
            cotizacion_id,
        )

        if existente is not None:

            raise ValueError(
                f"La cotización ya tiene el pedido "
                f"{existente.numero}.",
            )

        cotizacion = ServicioCotizacion.obtener_completa(
            cotizacion_id,
        )

        if cotizacion is None:

            raise ValueError(
                "No se encontró la cotización.",
            )

        ServicioCotizacion.exigir_aprobada(
            cotizacion,
        )

        cabecera = {
            "numero": cls.generar_numero(),
            "fecha": date.today(),
            "cotizacion_id": cotizacion.id,
            "cliente_id": cotizacion.cliente_id,
            "observaciones": cotizacion.observaciones,
            "vendedor": cotizacion.vendedor,
            "subtotal": cotizacion.subtotal,
            "total": cotizacion.total,
            "estado": "borrador",
            "activo": True,
        }

        lineas = [
            {
                "producto_id": detalle.producto_id,
                "producto_variante_id": detalle.producto_variante_id,
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "impuesto_id": detalle.impuesto_id,
                "precio_incluye_iva": detalle.precio_incluye_iva,
                "total_linea": detalle.total_linea,
            }
            for detalle in cotizacion.detalles
        ]

        pedido = cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

        vincular_cotizacion_pedido(
            cotizacion.id,
            pedido.id,
        )

        return pedido

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.repositorio.obtener_completa(
            id_registro,
        )

    @classmethod
    def validar_cabecera(
        cls,
        cabecera,
        id_registro=None,
    ):

        numero = str(
            cabecera.get(
                "numero",
                "",
            )
            or "",
        ).strip()

        if (
            not numero
            and id_registro is None
        ):

            numero = cls.generar_numero()

        if not numero:

            raise ValueError(
                "El número de pedido es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe un pedido con ese número.",
            )

        cliente_id = cabecera.get(
            "cliente_id",
        )

        if not cliente_id:

            raise ValueError(
                "Seleccione un cliente.",
            )

        cabecera["numero"] = numero

    @classmethod
    def validar_lineas(
        cls,
        lineas: list[dict],
    ) -> list[dict]:

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        return ServicioFacturaVenta.validar_lineas(
            lineas,
        )

    @classmethod
    def guardar_completa(
        cls,
        cabecera,
        lineas,
        id_registro=None,
    ):

        cls.validar_cabecera(
            cabecera,
            id_registro,
        )

        lineas = cls.validar_lineas(
            lineas,
        )

        subtotal, total = ServicioCotizacion._calcular_totales(
            lineas,
            None,
            None,
            None,
        )

        cabecera["subtotal"] = subtotal
        cabecera["total"] = total
        cabecera.setdefault(
            "estado",
            "borrador",
        )
        cabecera.setdefault(
            "activo",
            True,
        )

        if id_registro is None:

            return cls.repositorio.guardar_completa(
                cabecera,
                lineas,
            )

        cambios = cls.auditar_documento(
            id_registro,
            cabecera,
            lineas,
        )

        resultado = cls.repositorio.actualizar_completa(
            id_registro,
            cabecera,
            lineas,
        )

        cls.confirmar_auditoria_cabecera(
            id_registro,
            cambios,
        )

        return resultado

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def reservar_inventario(
        cls,
        id_registro: int,
        *,
        bodega_id: int | None = None,
    ):

        from aplicacion.modulos.ventas.pedidos.reservas import (
            ServicioReservaPedido,
        )

        return ServicioReservaPedido.reservar(
            id_registro,
            bodega_id=bodega_id,
        )

    @classmethod
    def liberar_reserva(
        cls,
        id_registro: int,
    ):

        from aplicacion.modulos.ventas.pedidos.reservas import (
            ServicioReservaPedido,
        )

        return ServicioReservaPedido.liberar(
            id_registro,
        )
