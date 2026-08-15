from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.modulos.ventas.pedidos.servicios import (
    ServicioPedido,
)
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.nucleo.documentos.trazabilidad import (
    vincular_cotizacion_remision,
    vincular_pedido_remision,
)

from .repositorio import RepositorioRemision


class ServicioRemision(ServicioBase):

    repositorio = RepositorioRemision

    entidad_auditoria = "RemisionVenta"

    modulo_auditoria = "ventas/remisiones"

    PREFIJO = "REM"

    LONGITUD = 6

    @classmethod
    def _prefijo(cls) -> str:

        return str(
            Configuracion.obtener(
                "ventas",
                "prefijo_remision_interna",
            )
            or Configuracion.obtener(
                "ventas",
                "prefijo_remision",
            )
            or cls.PREFIJO,
        )

    @classmethod
    def generar_numero(cls) -> str:

        prefijo = cls._prefijo()

        secuencia = cls.repositorio.siguiente_secuencia(
            prefijo,
        )

        return (
            f"{prefijo}"
            f"{secuencia:0{cls.LONGITUD}d}"
        )

    @classmethod
    def _lineas_desde_documento(
        cls,
        detalles,
    ) -> list[dict]:

        return [
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
            for detalle in detalles
        ]

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
                f"La cotización ya tiene la remisión "
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

        lineas = cls._lineas_desde_documento(
            cotizacion.detalles,
        )

        remision = cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

        vincular_cotizacion_remision(
            cotizacion.id,
            remision.id,
        )

        return remision

    @classmethod
    def crear_desde_pedido(
        cls,
        pedido_id: int,
    ):

        existente = cls.repositorio.obtener_por_pedido(
            pedido_id,
        )

        if existente is not None:

            raise ValueError(
                f"El pedido ya tiene la remisión "
                f"{existente.numero}.",
            )

        pedido = ServicioPedido.obtener_completa(
            pedido_id,
        )

        if pedido is None:

            raise ValueError(
                "No se encontró el pedido.",
            )

        if pedido.estado == "borrador":

            raise ValueError(
                "Confirme el pedido antes de remisionar.",
            )

        cabecera = {
            "numero": cls.generar_numero(),
            "fecha": date.today(),
            "pedido_id": pedido.id,
            "cotizacion_id": pedido.cotizacion_id,
            "cliente_id": pedido.cliente_id,
            "observaciones": pedido.observaciones,
            "vendedor": pedido.vendedor,
            "subtotal": pedido.subtotal,
            "total": pedido.total,
            "estado": "borrador",
            "activo": True,
        }

        lineas = cls._lineas_desde_documento(
            pedido.detalles,
        )

        remision = cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

        vincular_pedido_remision(
            pedido.id,
            remision.id,
        )

        if pedido.cotizacion_id:

            vincular_cotizacion_remision(
                pedido.cotizacion_id,
                remision.id,
            )

        return remision

    @classmethod
    def despachar(
        cls,
        id_registro: int,
    ):

        remision = cls.obtener_completa(
            id_registro,
        )

        if remision is None:

            raise ValueError(
                "No se encontró la remisión.",
            )

        if remision.inventario_aplicado:

            raise ValueError(
                "La remisión ya fue despachada.",
            )

        if remision.estado == "borrador":

            raise ValueError(
                "Confirme la remisión antes de despachar.",
            )

        ServicioInventario.registrar_salida_remision(
            remision,
        )

        return cls.repositorio.actualizar_despacho(
            id_registro,
        )

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
                "El número de remisión es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una remisión con ese número.",
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
