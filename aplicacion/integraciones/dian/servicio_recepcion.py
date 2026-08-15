from __future__ import annotations

import tempfile
from datetime import date, timedelta
from pathlib import Path

from aplicacion.integraciones.dian.cliente_recepcion import (
    ClienteRecepcionDian,
)
from aplicacion.integraciones.dian.importador_xml import (
    copiar_xml_almacen,
    parsear_factura_xml_texto,
)
from aplicacion.integraciones.dian.modelos_recepcion import (
    ResultadoSincronizacionCompras,
)
from aplicacion.nucleo.configuracion import Configuracion

from aplicacion.modulos.compras.facturas.integracion import (
    IntegracionFacturaCompra,
)

from aplicacion.modulos.compras.facturas.servicios import (
    ServicioFacturaCompra,
)


class ServicioRecepcionCompras:
    """
    Sincroniza facturas de compra recibidas desde un
    proveedor API DIAN (token Bearer).
    """

    @classmethod
    def _auto_validar_cufe(cls) -> bool:

        config = (
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {}
        )

        return bool(
            config.get(
                "auto_validar_cufe",
                True,
            )
        )

    @classmethod
    def _config(cls) -> dict:

        return dict(
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {},
        )

    @classmethod
    def _estado_inicial_sync(cls) -> str:

        if cls._config().get(
            "modo_automatico",
            False,
        ):

            return "pendiente_revision"

        return "recibida"

    @classmethod
    def sincronizar(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> ResultadoSincronizacionCompras:

        if not ClienteRecepcionDian.habilitado():

            return ResultadoSincronizacionCompras(
                mensaje=(
                    "Active dian.recepcion_compras.habilitado "
                    "en configuración."
                ),
                errores=[
                    "Recepción DIAN deshabilitada.",
                ],
            )

        if fecha_hasta is None:

            fecha_hasta = date.today()

        if fecha_desde is None:

            fecha_desde = (
                fecha_hasta
                - timedelta(
                    days=ClienteRecepcionDian._dias_consulta(),
                )
            )

        importadas = 0
        omitidas = 0
        errores: list[str] = []
        facturas_ids: list[int] = []

        pagina = 1

        while True:

            try:

                documentos = ClienteRecepcionDian.listar_recibidos(
                    fecha_desde=fecha_desde,
                    fecha_hasta=fecha_hasta,
                    pagina=pagina,
                )

            except Exception as error:

                return ResultadoSincronizacionCompras(
                    importadas=importadas,
                    omitidas=omitidas,
                    errores=errores
                    + [str(error)],
                    mensaje=(
                        "La sincronización se detuvo "
                        "por un error de conexión."
                    ),
                )

            if not documentos:

                break

            for documento in documentos:

                cufe = (
                    documento.cufe
                    or documento.track_id
                )

                if (
                    cufe
                    and ServicioFacturaCompra.repositorio.existe_cufe(
                        cufe,
                    )
                ):

                    omitidas += 1

                    continue

                try:

                    xml = ClienteRecepcionDian.descargar_xml(
                        documento.track_id,
                    )

                    factura = cls.importar_desde_contenido_xml(
                        xml,
                        nombre_archivo=(
                            f"{documento.track_id[:16]}.xml"
                        ),
                    )

                except Exception as error:

                    referencia = (
                        documento.numero
                        or cufe[:16]
                        or documento.track_id[:16]
                    )

                    errores.append(
                        f"{referencia}: {error}",
                    )

                    continue

                importadas += 1

                facturas_ids.append(
                    factura.id,
                )

                if (
                    cls._auto_validar_cufe()
                    and factura.cufe
                ):

                    try:

                        IntegracionFacturaCompra.validar_cufe_online(
                            factura.id,
                        )

                    except ValueError:

                        pass

            if len(
                documentos,
            ) < ClienteRecepcionDian._pagina_tamano():

                break

            pagina += 1

        exito = importadas > 0 or (
            not errores
            and omitidas >= 0
        )

        mensaje = (
            f"Sincronización completada: "
            f"{importadas} importada(s), "
            f"{omitidas} omitida(s)."
        )

        if errores:

            mensaje = (
                f"{mensaje}\n"
                f"{len(errores)} documento(s) "
                f"con error."
            )

        return ResultadoSincronizacionCompras(
            exito=exito,
            importadas=importadas,
            omitidas=omitidas,
            errores=errores,
            mensaje=mensaje,
            facturas_ids=facturas_ids,
        )

    @classmethod
    def importar_desde_contenido_xml(
        cls,
        contenido_xml: str,
        *,
        nombre_archivo: str = "sync.xml",
    ):

        parseada = parsear_factura_xml_texto(
            contenido_xml,
        )

        if (
            parseada.cufe
            and ServicioFacturaCompra.repositorio.existe_cufe(
                parseada.cufe,
            )
        ):

            existente = (
                ServicioFacturaCompra.repositorio.obtener_por_cufe(
                    parseada.cufe,
                )
            )

            raise ValueError(
                f"El CUFE ya está registrado en la factura "
                f"{existente.numero}.",
            )

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            suffix=".xml",
            delete=False,
        ) as temporal:

            temporal.write(
                contenido_xml,
            )

            ruta_temporal = temporal.name

        try:

            ruta_almacen = copiar_xml_almacen(
                ruta_temporal,
                carpeta_destino=ServicioFacturaCompra.carpeta_xml(),
                cufe=parseada.cufe,
            )

        finally:

            Path(
                ruta_temporal,
            ).unlink(
                missing_ok=True,
            )

        proveedor = ServicioFacturaCompra.asegurar_proveedor(
            parseada.nit_proveedor,
            parseada.razon_social_proveedor,
        )

        lineas = ServicioFacturaCompra._lineas_desde_xml(
            parseada,
        )

        estado = cls._estado_inicial_sync()

        observaciones = (
            "Pendiente de revisión. "
            "Importada desde sincronización DIAN."
            if estado == "pendiente_revision"
            else "Importada desde sincronización DIAN."
        )

        cabecera = {
            "numero": ServicioFacturaCompra.generar_numero(),
            "fecha": parseada.fecha or date.today(),
            "proveedor_id": (
                proveedor.id
                if proveedor
                else None
            ),
            "nit_proveedor": parseada.nit_proveedor,
            "razon_social_proveedor": (
                parseada.razon_social_proveedor
            ),
            "numero_proveedor": parseada.numero_proveedor,
            "prefijo": parseada.prefijo,
            "consecutivo": parseada.consecutivo,
            "cufe": parseada.cufe,
            "subtotal": parseada.subtotal,
            "iva": parseada.iva,
            "total": parseada.total,
            "origen": "sync",
            "ruta_xml": ruta_almacen,
            "estado": estado,
            "observaciones": observaciones,
            "activo": True,
            **ServicioFacturaCompra._campos_acuse_desde_xml(
                parseada,
            ),
        }

        if proveedor:
            cabecera["retefuente_id"] = (
                proveedor.retefuente_id
            )
            cabecera["reteica_id"] = (
                proveedor.reteica_id
            )
            cabecera["reteiva_id"] = (
                proveedor.reteiva_id
            )

        factura = ServicioFacturaCompra.guardar_completa(
            cabecera,
            lineas,
        )

        factura = ServicioFacturaCompra._procesar_acuse_recibo(
            factura,
        )

        from aplicacion.modulos.compras.facturas.automatizacion import (
            ServicioAutomatizacionCompras,
        )

        if cls._config().get(
            "procesar_automatico",
            True,
        ):
            ServicioAutomatizacionCompras.procesar_factura(
                factura.id,
            )
            factura = ServicioFacturaCompra.obtener_completa(
                factura.id,
            )

        return factura
