from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.modulos.ventas.facturas.formatos_impresion import (
    formato_predeterminado_factura,
)
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.nucleo.documentos.trazabilidad import (
    vincular_cotizacion_factura,
    vincular_pedido_factura,
    vincular_pedido_remision,
    vincular_remision_factura,
)

from .repositorio import RepositorioFacturaVenta


class ServicioFacturaVenta(ServicioBase):

    repositorio = RepositorioFacturaVenta

    entidad_auditoria = "FacturaVenta"

    modulo_auditoria = "ventas/facturas"

    auditoria_campos_linea = [
        "producto_id",
        "producto_variante_id",
        "descripcion",
        "cantidad",
        "precio_unitario",
        "impuesto_id",
        "total_linea",
    ]

    auditoria_campos_cabecera_excluir = [
        "fecha_creacion",
        "fecha_actualizacion",
    ]

    PREFIJO = "FV"

    LONGITUD = 6

    @classmethod
    def _prefijo(cls) -> str:

        return str(
            Configuracion.obtener(
                "ventas",
                "prefijo_factura",
            )
            or cls.PREFIJO,
        )

    @classmethod
    def _longitud(cls) -> int:

        try:

            return int(
                Configuracion.obtener(
                    "ventas",
                    "longitud_secuencia",
                )
                or cls.LONGITUD,
            )

        except (
            TypeError,
            ValueError,
        ):

            return cls.LONGITUD

    @classmethod
    def generar_numero(cls) -> str:

        prefijo = cls._prefijo()

        secuencia = cls.repositorio.siguiente_secuencia(
            prefijo,
        )

        return (
            f"{prefijo}"
            f"{secuencia:0{cls._longitud()}d}"
        )

    @classmethod
    def _calcular_iva(
        cls,
        lineas: list[dict],
    ) -> tuple[float, float]:

        subtotal = 0.0
        iva = 0.0

        for linea in lineas:

            total_linea = float(
                linea.get(
                    "total_linea",
                    0,
                )
                or 0,
            )

            subtotal += total_linea

            impuesto_id = linea.get(
                "impuesto_id",
            )

            if not impuesto_id:

                continue

            impuesto = RepositorioImpuesto.obtener_por_id(
                impuesto_id,
            )

            if impuesto is None:

                continue

            porcentaje = float(
                impuesto.porcentaje or 0,
            )

            if porcentaje <= 0:

                continue

            if linea.get(
                "precio_incluye_iva",
            ):

                base = total_linea / (
                    1 + porcentaje / 100
                )

                iva += total_linea - base

            else:

                iva += (
                    total_linea
                    * porcentaje
                    / 100
                )

        return subtotal, iva

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
                f"La cotización ya tiene la factura "
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

        subtotal, iva = cls._calcular_iva(
            lineas,
        )

        cabecera_retenciones = {
            "retefuente_id": cotizacion.retefuente_id,
            "reteica_id": cotizacion.reteica_id,
            "reteiva_id": cotizacion.reteiva_id,
        }

        cls._aplicar_resumen(
            cabecera_retenciones,
            lineas,
        )

        secuencia = cls.repositorio.siguiente_secuencia(
            cls._prefijo(),
        )

        cabecera = {
            "numero": cls.generar_numero(),
            "prefijo": Configuracion.obtener(
                "dian",
                "prefijo_factura",
            )
            or "SETP",
            "consecutivo_dian": str(secuencia),
            "fecha": date.today(),
            "cliente_id": cotizacion.cliente_id,
            "cotizacion_id": cotizacion.id,
            "subtotal": cabecera_retenciones[
                "subtotal"
            ],
            "iva": cabecera_retenciones["iva"],
            "retefuente_id": cabecera_retenciones[
                "retefuente_id"
            ],
            "reteica_id": cabecera_retenciones[
                "reteica_id"
            ],
            "reteiva_id": cabecera_retenciones[
                "reteiva_id"
            ],
            "valor_retefuente": cabecera_retenciones[
                "valor_retefuente"
            ],
            "valor_reteica": cabecera_retenciones[
                "valor_reteica"
            ],
            "valor_reteiva": cabecera_retenciones[
                "valor_reteiva"
            ],
            "total": cabecera_retenciones["total"],
            "observaciones": cotizacion.observaciones,
            "formato_impresion": normalizar_formato_codigo(
                getattr(
                    cotizacion,
                    "formato_impresion",
                    None,
                )
                or formato_predeterminado_factura(),
            ),
            "estado": "borrador",
            "activo": True,
        }

        return cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

    @classmethod
    def crear_desde_pedido(
        cls,
        pedido_id: int,
    ):

        from aplicacion.modulos.ventas.pedidos.servicios import (
            ServicioPedido,
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
                "Confirme el pedido antes de facturar.",
            )

        if pedido.cotizacion_id:

            existente = cls.repositorio.obtener_por_cotizacion(
                pedido.cotizacion_id,
            )

            if existente is not None:

                raise ValueError(
                    f"Ya existe la factura "
                    f"{existente.numero}.",
                )

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
            for detalle in pedido.detalles
        ]

        subtotal, iva = cls._calcular_iva(
            lineas,
        )

        secuencia = cls.repositorio.siguiente_secuencia(
            cls._prefijo(),
        )

        cabecera = {
            "numero": cls.generar_numero(),
            "prefijo": Configuracion.obtener(
                "dian",
                "prefijo_factura",
            )
            or "SETP",
            "consecutivo_dian": str(secuencia),
            "fecha": date.today(),
            "cliente_id": pedido.cliente_id,
            "cotizacion_id": pedido.cotizacion_id,
            "pedido_id": pedido.id,
            "subtotal": subtotal,
            "iva": iva,
            "total": float(
                pedido.total or 0,
            ),
            "observaciones": pedido.observaciones,
            "formato_impresion": cls._formato_desde_pedido(
                pedido,
            ),
            "estado": "borrador",
            "activo": True,
        }

        factura = cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

        vincular_pedido_factura(
            pedido.id,
            factura.id,
        )

        if pedido.cotizacion_id:

            vincular_cotizacion_factura(
                pedido.cotizacion_id,
                factura.id,
            )

        return factura

    @classmethod
    def crear_desde_remision(
        cls,
        remision_id: int,
    ):

        from aplicacion.modulos.ventas.remisiones.servicios import (
            ServicioRemision,
        )

        remision = ServicioRemision.obtener_completa(
            remision_id,
        )

        if remision is None:

            raise ValueError(
                "No se encontró la remisión.",
            )

        if remision.cotizacion_id:

            existente = cls.repositorio.obtener_por_cotizacion(
                remision.cotizacion_id,
            )

            if existente is not None:

                raise ValueError(
                    f"Ya existe la factura "
                    f"{existente.numero}.",
                )

        elif remision.pedido_id:

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

                existente = cls.repositorio.obtener_por_cotizacion(
                    pedido.cotizacion_id,
                )

                if existente is not None:

                    raise ValueError(
                        f"Ya existe la factura "
                        f"{existente.numero}.",
                    )

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
            for detalle in remision.detalles
        ]

        subtotal, iva = cls._calcular_iva(
            lineas,
        )

        secuencia = cls.repositorio.siguiente_secuencia(
            cls._prefijo(),
        )

        cabecera = {
            "numero": cls.generar_numero(),
            "prefijo": Configuracion.obtener(
                "dian",
                "prefijo_factura",
            )
            or "SETP",
            "consecutivo_dian": str(secuencia),
            "fecha": date.today(),
            "cliente_id": remision.cliente_id,
            "cotizacion_id": remision.cotizacion_id,
            "pedido_id": remision.pedido_id,
            "subtotal": subtotal,
            "iva": iva,
            "total": float(
                remision.total or 0,
            ),
            "observaciones": remision.observaciones,
            "formato_impresion": cls._formato_desde_remision(
                remision,
            ),
            "estado": "borrador",
            "activo": True,
        }

        factura = cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

        vincular_remision_factura(
            remision.id,
            factura.id,
        )

        if remision.pedido_id:

            vincular_pedido_factura(
                remision.pedido_id,
                factura.id,
            )

        if remision.cotizacion_id:

            vincular_cotizacion_factura(
                remision.cotizacion_id,
                factura.id,
            )

        return factura

    @classmethod
    def _formato_desde_remision(
        cls,
        remision,
    ) -> str:

        if remision.pedido_id:

            from aplicacion.modulos.ventas.pedidos.servicios import (
                ServicioPedido,
            )

            pedido = ServicioPedido.obtener_completa(
                remision.pedido_id,
            )

            if pedido is not None:

                return cls._formato_desde_pedido(
                    pedido,
                )

        if remision.cotizacion_id:

            cotizacion = ServicioCotizacion.obtener_completa(
                remision.cotizacion_id,
            )

            if cotizacion is not None:

                return normalizar_formato_codigo(
                    getattr(
                        cotizacion,
                        "formato_impresion",
                        None,
                    )
                    or formato_predeterminado_factura(),
                )

        return formato_predeterminado_factura()

    @classmethod
    def _formato_desde_pedido(
        cls,
        pedido,
    ) -> str:

        if pedido.cotizacion_id:

            cotizacion = ServicioCotizacion.obtener_completa(
                pedido.cotizacion_id,
            )

            if cotizacion is not None:

                return normalizar_formato_codigo(
                    getattr(
                        cotizacion,
                        "formato_impresion",
                        None,
                    )
                    or formato_predeterminado_factura(),
                )

        return formato_predeterminado_factura()

    @classmethod
    def actualizar_formato_impresion(
        cls,
        id_registro: int,
        formato: str,
    ):

        codigo = normalizar_formato_codigo(
            formato,
        )

        if codigo not in ServicioCotizacion.formatos_disponibles():

            raise ValueError(
                "Formato de impresión no válido.",
            )

        return cls.repositorio.actualizar_formato_impresion(
            id_registro,
            formato=codigo,
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
                "El número de factura es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una factura con ese número.",
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
    def _normalizar_retenciones(
        cls,
        cabecera: dict,
    ) -> None:

        for campo in (
            "retefuente_id",
            "reteica_id",
            "reteiva_id",
        ):

            valor = cabecera.get(
                campo,
            )

            if valor in (
                None,
                "",
                0,
                "0",
            ):

                cabecera[campo] = None

                continue

            try:

                cabecera[campo] = int(
                    valor,
                )

            except (
                TypeError,
                ValueError,
            ):

                cabecera[campo] = None

    @classmethod
    def _aplicar_resumen(
        cls,
        cabecera: dict,
        lineas: list[dict],
    ) -> None:

        cls._normalizar_retenciones(
            cabecera,
        )

        resumen = ServicioCotizacion._calcular_resumen(
            lineas,
            cabecera.get(
                "retefuente_id",
            ),
            cabecera.get(
                "reteica_id",
            ),
            cabecera.get(
                "reteiva_id",
            ),
        )

        cabecera["subtotal"] = resumen[
            "subtotal"
        ]
        cabecera["iva"] = resumen["iva"]
        cabecera["valor_retefuente"] = resumen[
            "retefuente"
        ]
        cabecera["valor_reteica"] = resumen[
            "reteica"
        ]
        cabecera["valor_reteiva"] = resumen[
            "reteiva"
        ]
        cabecera["total"] = resumen["total"]

    @classmethod
    def validar_lineas(
        cls,
        lineas: list[dict],
    ) -> list[dict]:

        lineas_validas: list[dict] = []

        for linea in lineas:

            descripcion = str(
                linea.get(
                    "descripcion",
                    "",
                )
                or "",
            ).strip()

            cantidad = float(
                linea.get(
                    "cantidad",
                    0,
                )
                or 0,
            )

            precio = float(
                linea.get(
                    "precio_unitario",
                    0,
                )
                or 0,
            )

            if (
                not descripcion
                or cantidad <= 0
            ):

                continue

            subtotal_linea, total_linea = (
                ServicioCotizacion._calcular_linea(
                    cantidad,
                    precio,
                    linea.get(
                        "impuesto_id",
                    ),
                    bool(
                        linea.get(
                            "precio_incluye_iva",
                            False,
                        )
                    ),
                )
            )

            lineas_validas.append(
                {
                    "producto_id": linea.get(
                        "producto_id",
                    ),
                    "producto_variante_id": linea.get(
                        "producto_variante_id",
                    ),
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "impuesto_id": linea.get(
                        "impuesto_id",
                    ),
                    "precio_incluye_iva": bool(
                        linea.get(
                            "precio_incluye_iva",
                            False,
                        )
                    ),
                    "total_linea": total_linea,
                },
            )

        if not lineas_validas:

            raise ValueError(
                "Agregue al menos una línea con producto, "
                "cantidad y precio válidos.",
            )

        return lineas_validas

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

        cliente_id = cabecera.get(
            "cliente_id",
        )

        if (
            cliente_id
            and not cabecera.get(
                "fecha_vencimiento",
            )
        ):

            from aplicacion.maestros.terceros.repositorio import (
                TerceroRepositorio,
            )

            from aplicacion.modulos.cartera.utilidades import (
                calcular_fecha_vencimiento,
            )

            cliente = (
                TerceroRepositorio.obtener_por_id(
                    cliente_id,
                )
            )

            cabecera[
                "fecha_vencimiento"
            ] = calcular_fecha_vencimiento(
                cabecera.get(
                    "fecha",
                )
                or date.today(),
                (
                    cliente.dias_credito
                    if cliente
                    else 0
                ),
            )

        lineas = cls.validar_lineas(
            lineas,
        )

        cls._aplicar_resumen(
            cabecera,
            lineas,
        )

        total = float(
            cabecera["total"],
        )

        vendedor = str(
            cabecera.pop(
                "vendedor",
                "",
            )
            or "",
        ).strip()

        observaciones = str(
            cabecera.get(
                "observaciones",
                "",
            )
            or "",
        ).strip()

        if vendedor:

            prefijo = f"Vendedor: {vendedor}"

            if observaciones:

                observaciones = (
                    f"{prefijo}\n{observaciones}"
                )

            else:

                observaciones = prefijo

        cabecera["observaciones"] = observaciones

        cabecera.setdefault(
            "estado",
            "borrador",
        )
        cabecera.setdefault(
            "activo",
            True,
        )
        cabecera.setdefault(
            "formato_impresion",
            formato_predeterminado_factura(),
        )
        cabecera.setdefault(
            "valor_pagado",
            0,
        )
        cabecera.setdefault(
            "saldo_pendiente",
            total,
        )
        cabecera.setdefault(
            "estado_pago",
            "pendiente",
        )

        if id_registro is None:

            secuencia = cls.repositorio.siguiente_secuencia(
                cls._prefijo(),
            )

            cabecera.setdefault(
                "prefijo",
                Configuracion.obtener(
                    "dian",
                    "prefijo_factura",
                )
                or "SETP",
            )

            cabecera.setdefault(
                "consecutivo_dian",
                str(secuencia),
            )

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
