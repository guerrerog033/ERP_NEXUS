from __future__ import annotations

from pathlib import Path

from aplicacion.integraciones.dian.cliente_emision import (
    ClienteEmisionDian,
)
from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.integraciones.dian.generador_xml import (
    GeneradorXmlFactura,
)
from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioFacturaVenta
from .servicios import ServicioFacturaVenta


class IntegracionFacturaVenta:

    @classmethod
    def aplicar_inventario(
        cls,
        id_registro: int,
    ) -> list:

        factura = ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.inventario_aplicado:

            return []

        from aplicacion.modulos.inventario.servicios import (
            ServicioInventario,
        )

        return (
            ServicioInventario.registrar_salida_factura_venta(
                factura,
            )
        )

    @classmethod
    def confirmar_venta(
        cls,
        id_registro: int,
        *,
        emitir_dian: bool = False,
    ):

        factura = ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.estado == "borrador":

            RepositorioFacturaVenta.actualizar_estado_confirmacion(
                id_registro,
                estado="generada",
            )

        cls.aplicar_inventario(
            id_registro,
        )

        if emitir_dian:

            factura = ServicioFacturaVenta.obtener_completa(
                id_registro,
            )

            if (
                factura is not None
                and factura.estado
                not in (
                    "emitida",
                )
            ):

                cls.emitir_electronica(
                    id_registro,
                )

        else:

            cls._contabilizar_si_configurado(
                id_registro,
            )

        return ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

    @classmethod
    def emitir_electronica(
        cls,
        id_registro: int,
    ):

        factura = ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.estado == "emitida":

            raise ValueError(
                "La factura ya fue emitida.",
            )

        datos = GeneradorXmlFactura.generar(
            factura,
        )

        xml_final = datos.xml
        mensaje_firma = ""

        try:

            xml_final = FirmadorXml.firmar(
                datos.xml,
                ruta_salida=datos.ruta_xml,
            )

        except ValueError as error:

            if Configuracion.obtener(
                "dian",
                "certificado_ruta",
            ):

                raise

            mensaje_firma = str(error)

        nombre_xml = Path(
            datos.ruta_xml,
        ).name

        from aplicacion.integraciones.dian.contenedor_electronico import (
            adjuntos_contenedor_factura_venta,
        )

        resultado = ClienteEmisionDian.enviar(
            nombre_xml=nombre_xml,
            xml_firmado=xml_final,
            adjuntos_contenedor=adjuntos_contenedor_factura_venta(
                factura,
                nombre_xml=nombre_xml,
                cufe=datos.cufe,
            ),
        )

        estado = "emitida"

        if resultado.exito:

            estado_dian = "aceptada"

        elif resultado.estado:

            estado_dian = resultado.estado

        else:

            estado_dian = "pendiente"

        if (
            not resultado.exito
            and not Configuracion.obtener(
                "dian",
                "certificado_ruta",
            )
        ):

            estado = "generada"
            estado_dian = "sin_firma"

        mensaje = resultado.mensaje or mensaje_firma

        if resultado.error and not mensaje:

            mensaje = resultado.error

        RepositorioFacturaVenta.actualizar_emision(
            id_registro,
            cufe=datos.cufe,
            estado=estado,
            estado_dian=estado_dian,
            mensaje_dian=mensaje or "",
            ruta_xml=datos.ruta_xml,
            ruta_zip=resultado.ruta_zip,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

        if (
            resultado.exito
            or estado == "emitida"
        ):

            cls.aplicar_inventario(
                id_registro,
            )

        cls._contabilizar_si_configurado(
            id_registro,
        )

        return resultado

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        factura = ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.contabilizado:

            raise ValueError(
                "La factura ya está contabilizada.",
            )

        if factura.estado in (
            "borrador",
        ):

            raise ValueError(
                "Emita o genere la factura antes "
                "de contabilizar.",
            )

        asiento = ServicioContabilidad.registrar_factura_venta(
            factura,
        )

        RepositorioFacturaVenta.actualizar_contabilizacion(
            id_registro,
            asiento_id=asiento.id,
        )

        return asiento

    @classmethod
    def _contabilizar_si_configurado(
        cls,
        id_registro: int,
    ) -> None:

        if not Configuracion.obtener(
            "ventas",
            "contabilizar_automatico",
        ):

            return

        try:

            cls.contabilizar(
                id_registro,
            )

        except ValueError:

            pass

    @classmethod
    def facturar_cotizacion(
        cls,
        cotizacion_id: int,
    ):

        factura = ServicioFacturaVenta.crear_desde_cotizacion(
            cotizacion_id,
        )

        resultado = cls.emitir_electronica(
            factura.id,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            factura.id,
        )

        return factura, resultado

    @classmethod
    def facturar_pedido(
        cls,
        pedido_id: int,
    ):

        factura = ServicioFacturaVenta.crear_desde_pedido(
            pedido_id,
        )

        resultado = cls.emitir_electronica(
            factura.id,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            factura.id,
        )

        return factura, resultado

    @classmethod
    def abrir_formulario_factura(
        cls,
        id_registro: int,
        *,
        parent=None,
        titulo: str | None = None,
    ) -> None:

        from .dialogo_formulario import (
            mostrar_formulario_factura,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            id_registro,
        )

        if titulo is None:

            if factura is not None:

                titulo = (
                    f"Factura {factura.numero}"
                )

            else:

                titulo = "Factura de venta"

        mostrar_formulario_factura(
            id_registro,
            parent=parent,
            titulo=titulo,
        )

    @classmethod
    def _manejar_factura_existente(
        cls,
        factura,
        parent,
    ) -> None:

        from PySide6.QtWidgets import (
            QMessageBox,
        )

        from aplicacion.framework.ui.vista_documento import (
            mostrar_dialogo_vista,
        )
        from aplicacion.modulos.ventas.facturas.vista_factura import (
            VistaFacturaVenta,
        )

        abrir = QMessageBox.question(
            parent,
            "Facturar",
            f"Ya existe la factura "
            f"{factura.numero} "
            f"({factura.estado}).\n\n"
            "¿Desea abrirla?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            abrir
            != QMessageBox.StandardButton.Yes
        ):

            return

        mostrar_dialogo_vista(
            VistaFacturaVenta,
            factura.id,
            titulo=f"Factura {factura.numero}",
            parent=parent,
        )

    @classmethod
    def _iniciar_facturacion(
        cls,
        *,
        parent,
        obtener_existente,
        crear_borrador,
        titulo_nueva: str,
    ) -> None:

        from PySide6.QtWidgets import (
            QMessageBox,
        )

        existente = obtener_existente()

        if existente is not None:

            cls._manejar_factura_existente(
                existente,
                parent,
            )

            return

        try:

            factura = crear_borrador()

        except ValueError as error:

            QMessageBox.warning(
                parent,
                "Facturar",
                str(
                    error,
                ),
            )

            return

        cls.abrir_formulario_factura(
            factura.id,
            parent=parent,
            titulo=(
                f"{titulo_nueva} — "
                f"{factura.numero}"
            ),
        )

    @classmethod
    def iniciar_facturacion_desde_cotizacion(
        cls,
        cotizacion_id: int,
        parent,
    ) -> None:

        cls._iniciar_facturacion(
            parent=parent,
            obtener_existente=lambda: (
                RepositorioFacturaVenta.obtener_por_cotizacion(
                    cotizacion_id,
                )
            ),
            crear_borrador=lambda: (
                ServicioFacturaVenta.crear_desde_cotizacion(
                    cotizacion_id,
                )
            ),
            titulo_nueva="Nueva factura",
        )

    @classmethod
    def iniciar_facturacion_desde_pedido(
        cls,
        pedido_id: int,
        parent,
    ) -> None:

        from aplicacion.modulos.ventas.pedidos.servicios import (
            ServicioPedido,
        )

        def obtener_existente():

            pedido = ServicioPedido.obtener_completa(
                pedido_id,
            )

            if (
                pedido is not None
                and pedido.cotizacion_id
            ):

                return (
                    RepositorioFacturaVenta.obtener_por_cotizacion(
                        pedido.cotizacion_id,
                    )
                )

            return None

        cls._iniciar_facturacion(
            parent=parent,
            obtener_existente=obtener_existente,
            crear_borrador=lambda: (
                ServicioFacturaVenta.crear_desde_pedido(
                    pedido_id,
                )
            ),
            titulo_nueva="Nueva factura",
        )

    @classmethod
    def iniciar_facturacion_desde_remision(
        cls,
        remision_id: int,
        parent,
    ) -> None:

        from aplicacion.modulos.ventas.remisiones.servicios import (
            ServicioRemision,
        )

        def obtener_existente():

            remision = ServicioRemision.obtener_completa(
                remision_id,
            )

            if remision is None:

                return None

            if remision.cotizacion_id:

                return (
                    RepositorioFacturaVenta.obtener_por_cotizacion(
                        remision.cotizacion_id,
                    )
                )

            if remision.pedido_id:

                from aplicacion.modulos.ventas.pedidos.servicios import (
                    ServicioPedido,
                )

                pedido = ServicioPedido.obtener_completa(
                    remision.pedido_id,
                )

                if (
                    pedido is not None
                    and pedido.cotizacion_id
                ):

                    return (
                        RepositorioFacturaVenta.obtener_por_cotizacion(
                            pedido.cotizacion_id,
                        )
                    )

            return None

        cls._iniciar_facturacion(
            parent=parent,
            obtener_existente=obtener_existente,
            crear_borrador=lambda: (
                ServicioFacturaVenta.crear_desde_remision(
                    remision_id,
                )
            ),
            titulo_nueva="Nueva factura",
        )
