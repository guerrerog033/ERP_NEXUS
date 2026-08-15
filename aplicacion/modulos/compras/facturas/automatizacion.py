from __future__ import annotations

from dataclasses import dataclass, field

from aplicacion.nucleo.configuracion import Configuracion

from .emparejador_productos import EmparejadorProductosFactura
from .integracion import IntegracionFacturaCompra
from .repositorio import RepositorioFacturaCompra
from .servicios import ServicioFacturaCompra


@dataclass
class ResultadoAutomatizacionCompra:
    factura_id: int
    aprobada: bool = False
    cufe_validado: bool = False
    productos_emparejados: int = 0
    contabilizada: bool = False
    estado_final: str = ""
    errores: list[str] = field(
        default_factory=list,
    )


class ServicioAutomatizacionCompras:
    """Orquesta el flujo completo de facturas recibidas."""

    @classmethod
    def _config(cls, clave: str, defecto=False):
        return Configuracion.obtener(
            "compras",
            clave,
            defecto,
        )

    @classmethod
    def procesar_factura(
        cls,
        factura_id: int,
    ) -> ResultadoAutomatizacionCompra:
        resultado = ResultadoAutomatizacionCompra(
            factura_id=factura_id,
        )

        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if factura is None:
            resultado.errores.append(
                "Factura no encontrada.",
            )
            return resultado

        if factura.estado == "contabilizada":
            resultado.contabilizada = True
            resultado.estado_final = factura.estado
            return resultado

        if (
            factura.estado == "pendiente_revision"
            and cls._config(
                "aprobar_automatico",
                True,
            )
        ):
            try:
                IntegracionFacturaCompra.aprobar_revision(
                    factura_id,
                )
                resultado.aprobada = True
            except ValueError as error:
                resultado.errores.append(
                    str(error),
                )

        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if (
            factura
            and factura.cufe
            and cls._config(
                "auto_validar_cufe",
                True,
            )
            and not factura.cufe_validado
        ):
            try:
                IntegracionFacturaCompra.validar_cufe_online(
                    factura_id,
                )
                resultado.cufe_validado = True
            except ValueError as error:
                resultado.errores.append(
                    f"CUFE: {error}",
                )

        if cls._config(
            "emparejar_productos_automatico",
            True,
        ):
            resultado.productos_emparejados = (
                cls.emparejar_productos(
                    factura_id,
                )
            )

        from aplicacion.modulos.compras.integracion_oc import (
            ServicioIntegracionCompras,
        )

        ServicioIntegracionCompras.auto_vincular_orden(
            factura_id,
        )

        ServicioIntegracionCompras.evaluar_match(
            factura_id,
            persistir=True,
        )

        cls.aplicar_retenciones_proveedor(
            factura_id,
        )

        if cls._config(
            "contabilizar_automatico",
            True,
        ):
            if cls._puede_contabilizar(
                factura_id,
            ):
                try:
                    IntegracionFacturaCompra.contabilizar(
                        factura_id,
                    )
                    resultado.contabilizada = True
                except ValueError as error:
                    resultado.errores.append(
                        str(error),
                    )

        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if factura is not None:
            resultado.estado_final = factura.estado

        return resultado

    @classmethod
    def procesar_lote(
        cls,
        facturas_ids: list[int],
    ) -> list[ResultadoAutomatizacionCompra]:
        return [
            cls.procesar_factura(
                factura_id,
            )
            for factura_id in facturas_ids
        ]

    @classmethod
    def _puede_contabilizar(
        cls,
        factura_id: int,
    ) -> bool:
        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if factura is None:
            return False

        if factura.estado in (
            "contabilizada",
            "pendiente_revision",
        ):
            return False

        if (
            factura.cufe
            and Configuracion.obtener(
                "compras",
                "exigir_cufe_validado_contabilizar",
            )
            and not factura.cufe_validado
        ):
            return False

        if cls._config(
            "exigir_productos_emparejados",
            False,
        ):
            for detalle in factura.detalles:
                if not detalle.producto_id:
                    return False

        if (
            cls._config(
                "exigir_match_oc_contabilizar",
                False,
            )
            and factura.orden_compra_id
        ):
            from aplicacion.modulos.compras.integracion_oc import (
                ServicioIntegracionCompras,
            )

            match = ServicioIntegracionCompras.evaluar_match(
                factura_id,
            )

            if match.estado != "ok":
                return False

        return True

    @classmethod
    def emparejar_productos(
        cls,
        factura_id: int,
    ) -> int:
        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if factura is None:
            return 0

        lineas = []
        emparejadas = 0

        for detalle in factura.detalles:
            linea = {
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "impuesto_id": detalle.impuesto_id,
                "precio_incluye_iva": detalle.precio_incluye_iva,
                "total_linea": detalle.total_linea,
                "producto_id": detalle.producto_id,
                "producto_variante_id": detalle.producto_variante_id,
                "codigo_referencia": getattr(
                    detalle,
                    "codigo_referencia",
                    "",
                ),
            }

            if linea["producto_id"]:
                lineas.append(linea)
                continue

            codigo = str(
                linea.get(
                    "codigo_referencia",
                    "",
                )
                or "",
            )

            producto_id, variante_id = (
                EmparejadorProductosFactura.emparejar_linea(
                    codigo=codigo,
                    descripcion=linea["descripcion"],
                )
            )

            if producto_id:
                linea["producto_id"] = producto_id
                linea["producto_variante_id"] = variante_id
                emparejadas += 1

            lineas.append(linea)

        if emparejadas <= 0:
            return 0

        cabecera = {
            "numero": factura.numero,
            "fecha": factura.fecha,
            "proveedor_id": factura.proveedor_id,
            "nit_proveedor": factura.nit_proveedor,
            "razon_social_proveedor": (
                factura.razon_social_proveedor
            ),
            "numero_proveedor": factura.numero_proveedor,
            "prefijo": factura.prefijo,
            "consecutivo": factura.consecutivo,
            "cufe": factura.cufe,
            "subtotal": factura.subtotal,
            "iva": factura.iva,
            "total": factura.total,
            "retefuente_id": factura.retefuente_id,
            "reteica_id": factura.reteica_id,
            "reteiva_id": factura.reteiva_id,
            "valor_retefuente": factura.valor_retefuente,
            "valor_reteica": factura.valor_reteica,
            "valor_reteiva": factura.valor_reteiva,
            "estado": factura.estado,
            "observaciones": factura.observaciones,
            "activo": factura.activo,
        }

        ServicioFacturaCompra.guardar_completa(
            cabecera,
            lineas,
            factura_id,
        )

        return emparejadas

    @classmethod
    def aplicar_retenciones_proveedor(
        cls,
        factura_id: int,
    ) -> None:
        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if (
            factura is None
            or not factura.proveedor_id
        ):
            return

        if (
            factura.retefuente_id
            or factura.reteica_id
            or factura.reteiva_id
        ):
            return

        from aplicacion.maestros.terceros.repositorio import (
            TerceroRepositorio,
        )

        proveedor = TerceroRepositorio.obtener_por_id(
            factura.proveedor_id,
        )

        if proveedor is None:
            return

        cabecera = {
            "numero": factura.numero,
            "fecha": factura.fecha,
            "proveedor_id": factura.proveedor_id,
            "retefuente_id": proveedor.retefuente_id,
            "reteica_id": proveedor.reteica_id,
            "reteiva_id": proveedor.reteiva_id,
            "estado": factura.estado,
            "activo": factura.activo,
        }

        lineas = [
            {
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "impuesto_id": detalle.impuesto_id,
                "precio_incluye_iva": (
                    detalle.precio_incluye_iva
                ),
                "total_linea": detalle.total_linea,
                "producto_id": detalle.producto_id,
                "producto_variante_id": (
                    detalle.producto_variante_id
                ),
            }
            for detalle in factura.detalles
        ]

        ServicioFacturaCompra.guardar_completa(
            cabecera,
            lineas,
            factura_id,
        )

    @classmethod
    def contabilizar_automatico(
        cls,
        factura_id: int,
    ) -> None:
        if not cls._config(
            "contabilizar_automatico",
            True,
        ):
            return

        try:
            cls.procesar_factura(
                factura_id,
            )
        except ValueError:
            pass
