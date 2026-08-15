from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.integraciones.dian.importador_xml import (
    FacturaXmlParseada,
    copiar_xml_almacen,
    parsear_factura_xml,
)
from aplicacion.maestros.impuestos.iva_catalogo import (
    CODIGO_IVA_PREDETERMINADO,
)
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)
from aplicacion.maestros.terceros.modelos import Tercero
from aplicacion.maestros.terceros.repositorio import (
    TerceroRepositorio,
)
from aplicacion.nucleo.configuracion import Configuracion

from .emparejador_productos import EmparejadorProductosFactura
from .repositorio import RepositorioFacturaCompra


class ServicioFacturaCompra(ServicioBase):

    repositorio = RepositorioFacturaCompra

    entidad_auditoria = "FacturaCompra"

    modulo_auditoria = "compras/facturas"

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

    PREFIJO = "FC"

    LONGITUD = 6

    @classmethod
    def generar_numero(cls) -> str:

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        return ServicioNumeracion.siguiente_numero(
            "factura_compra",
            cls.PREFIJO,
            longitud=cls.LONGITUD,
        )

    @classmethod
    def carpeta_xml(cls) -> Path:

        ruta = Configuracion.obtener(
            "compras",
            "carpeta_xml",
        )

        if not ruta:

            ruta = "aplicacion/recursos/xml/facturas_compra"

        return Path(ruta)

    @classmethod
    def _porcentaje_impuesto(
        cls,
        impuesto_id,
    ) -> float:

        if not impuesto_id:

            return 0.0

        impuesto = RepositorioImpuesto.obtener_por_id(
            impuesto_id,
        )

        if impuesto is None:

            return 0.0

        return float(
            impuesto.porcentaje
            or 0,
        )

    @classmethod
    def _codigo_iva_por_porcentaje(
        cls,
        porcentaje: float,
    ) -> str:

        if porcentaje >= 18:

            return "IVA19"

        if porcentaje >= 4:

            return "IVA5"

        return "EXE0"

    @classmethod
    def _impuesto_id_por_porcentaje(
        cls,
        porcentaje: float,
    ):

        codigo = cls._codigo_iva_por_porcentaje(
            porcentaje,
        )

        impuesto = RepositorioImpuesto.obtener_por_codigo(
            codigo,
        )

        if impuesto is not None:

            return impuesto.id

        predeterminado = RepositorioImpuesto.obtener_por_codigo(
            CODIGO_IVA_PREDETERMINADO,
        )

        if predeterminado is None:

            return None

        return predeterminado.id

    @classmethod
    def _calcular_linea(
        cls,
        cantidad: float,
        precio: float,
        impuesto_id=None,
        precio_incluye_iva=False,
    ) -> tuple[float, float]:

        from aplicacion.dominio.impuestos.linea import calcular_linea

        return calcular_linea(
            cantidad,
            precio,
            cls._porcentaje_impuesto(
                impuesto_id,
            ),
            precio_incluye_iva=precio_incluye_iva,
        )

    @classmethod
    def _calcular_totales(
        cls,
        lineas: list[dict],
    ) -> tuple[float, float, float]:

        from aplicacion.dominio.impuestos.totales import calcular_totales_lineas

        return calcular_totales_lineas(
            lineas,
            lambda linea: cls._porcentaje_impuesto(
                linea.get(
                    "impuesto_id",
                ),
            ),
        )

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

        from aplicacion.modulos.ventas.cotizaciones.servicios import (
            ServicioCotizacion,
        )

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
        lineas,
    ):

        if not lineas:

            raise ValueError(
                "Agregue al menos una línea a la factura.",
            )

        lineas_validas = []

        for linea in lineas:

            descripcion = str(
                linea.get(
                    "descripcion",
                    "",
                )
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

            lineas_validas.append(
                {
                    "producto_id": linea.get(
                        "producto_id",
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
                }
            )

        if not lineas_validas:

            raise ValueError(
                "Las líneas deben tener descripción, "
                "cantidad y precio válidos.",
            )

        return lineas_validas

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
        ).strip()

        if (
            not numero
            and id_registro is None
        ):

            numero = cls.generar_numero()

        if not numero:

            raise ValueError(
                "El número interno es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una factura con ese número interno.",
            )

        proveedor_id = cabecera.get(
            "proveedor_id",
        )

        nit = str(
            cabecera.get(
                "nit_proveedor",
                "",
            )
        ).strip()

        if (
            not proveedor_id
            and not nit
        ):

            raise ValueError(
                "Seleccione un proveedor o indique el NIT.",
            )

        cufe = str(
            cabecera.get(
                "cufe",
                "",
            )
        ).strip()

        if cufe and cls.repositorio.existe_cufe(
            cufe,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una factura registrada con ese CUFE.",
            )

        fecha = cabecera.get(
            "fecha",
        )

        if fecha is None:

            fecha = date.today()

        cabecera["numero"] = numero
        cabecera["fecha"] = fecha
        cabecera["proveedor_id"] = (
            int(proveedor_id)
            if proveedor_id
            else None
        )
        cabecera["nit_proveedor"] = re.sub(
            r"\D",
            "",
            nit,
        )
        cabecera["razon_social_proveedor"] = str(
            cabecera.get(
                "razon_social_proveedor",
                "",
            )
        ).strip()
        cabecera["numero_proveedor"] = str(
            cabecera.get(
                "numero_proveedor",
                "",
            )
        ).strip()
        cabecera["prefijo"] = str(
            cabecera.get(
                "prefijo",
                "",
            )
        ).strip()
        cabecera["consecutivo"] = str(
            cabecera.get(
                "consecutivo",
                "",
            )
        ).strip()
        cabecera["cufe"] = cufe or None
        cabecera["observaciones"] = str(
            cabecera.get(
                "observaciones",
                "",
            )
        ).strip()
        cabecera["origen"] = str(
            cabecera.get(
                "origen",
                "manual",
            )
        ).strip() or "manual"
        cabecera["estado"] = str(
            cabecera.get(
                "estado",
                "recibida",
            )
        ).strip() or "recibida"
        cabecera["activo"] = bool(
            cabecera.get(
                "activo",
                True,
            )
        )

        return cabecera

    @classmethod
    def _buscar_proveedor_por_nit(
        cls,
        nit: str,
    ):

        nit = re.sub(
            r"\D",
            "",
            nit,
        )

        if not nit:

            return None

        db = TerceroRepositorio.obtener_sesion()

        try:

            return (
                db.query(Tercero)
                .filter(
                    Tercero.numero_documento == nit,
                    Tercero.tipo_tercero == "Proveedor",
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def _crear_proveedor_automatico_habilitado(cls) -> bool:

        if Configuracion.obtener(
            "compras",
            "crear_proveedor_automatico",
        ) is not None:

            return bool(
                Configuracion.obtener(
                    "compras",
                    "crear_proveedor_automatico",
                ),
            )

        recepcion = (
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {}
        )

        return bool(
            recepcion.get(
                "crear_proveedor_automatico",
                True,
            ),
        )

    @classmethod
    def _buscar_tercero_por_numero(
        cls,
        nit: str,
    ):

        nit = re.sub(
            r"\D",
            "",
            nit,
        )

        if not nit:

            return None

        db = TerceroRepositorio.obtener_sesion()

        try:

            return (
                db.query(Tercero)
                .filter(
                    Tercero.numero_documento == nit,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def _tipo_documento_por_numero(
        cls,
        nit: str,
    ) -> str:

        nit = re.sub(
            r"\D",
            "",
            nit,
        )

        if len(nit) >= 9:

            return "NIT"

        return "CC"

    @classmethod
    def asegurar_proveedor(
        cls,
        nit: str,
        razon_social: str = "",
    ):

        nit = re.sub(
            r"\D",
            "",
            str(
                nit or "",
            ),
        )

        if not nit:

            return None

        proveedor = cls._buscar_proveedor_por_nit(
            nit,
        )

        if proveedor is not None:

            return proveedor

        existente = cls._buscar_tercero_por_numero(
            nit,
        )

        if existente is not None:

            if existente.tipo_tercero != "Proveedor":

                from aplicacion.maestros.terceros.servicio import (
                    TerceroServicio,
                )

                datos = {
                    "tipo_tercero": "Proveedor",
                    "tipo_documento": (
                        existente.tipo_documento
                        or cls._tipo_documento_por_numero(
                            nit,
                        )
                    ),
                    "numero_documento": nit,
                    "razon_social": (
                        razon_social
                        or existente.razon_social
                        or f"Proveedor {nit}"
                    ),
                    "nombre_comercial": (
                        existente.nombre_comercial
                        or razon_social
                        or "",
                    ),
                    "activo": True,
                    "resp_r99_pn": True,
                }

                try:

                    return TerceroServicio.actualizar(
                        existente.id,
                        datos,
                    )

                except ValueError:

                    pass

            return existente

        if not cls._crear_proveedor_automatico_habilitado():

            return None

        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        try:

            return TerceroServicio.guardar(
                {
                    "tipo_tercero": "Proveedor",
                    "tipo_documento": cls._tipo_documento_por_numero(
                        nit,
                    ),
                    "numero_documento": nit,
                    "razon_social": (
                        razon_social
                        or f"Proveedor {nit}"
                    ),
                    "nombre_comercial": (
                        razon_social
                        or "",
                    ),
                    "activo": True,
                    "resp_r99_pn": True,
                },
            )

        except ValueError:

            return cls._buscar_proveedor_por_nit(
                nit,
            ) or cls._buscar_tercero_por_numero(
                nit,
            )

    @classmethod
    def _lineas_desde_xml(
        cls,
        parseada: FacturaXmlParseada,
    ) -> list[dict]:

        lineas = []

        for linea in parseada.lineas:

            impuesto_id = cls._impuesto_id_por_porcentaje(
                linea.porcentaje_iva,
            )

            producto_id = None
            producto_variante_id = None

            if Configuracion.obtener(
                "compras",
                "emparejar_productos_automatico",
                True,
            ):
                producto_id, producto_variante_id = (
                    EmparejadorProductosFactura.emparejar_linea(
                        codigo=linea.codigo_producto,
                        codigo_barras=linea.codigo_barras,
                        referencia=linea.referencia,
                        descripcion=linea.descripcion,
                    )
                )

            lineas.append(
                {
                    "descripcion": linea.descripcion,
                    "cantidad": linea.cantidad,
                    "precio_unitario": linea.precio_unitario,
                    "impuesto_id": impuesto_id,
                    "precio_incluye_iva": False,
                    "total_linea": linea.total_linea,
                    "producto_id": producto_id,
                    "producto_variante_id": producto_variante_id,
                    "codigo_referencia": (
                        linea.referencia
                        or linea.codigo_producto
                    ),
                }
            )

        return lineas

    @classmethod
    def _campos_acuse_desde_xml(
        cls,
        parseada: FacturaXmlParseada,
    ) -> dict:

        from aplicacion.integraciones.dian.servicio_acuse_recibo import (
            ServicioAcuseRecibo,
        )

        return ServicioAcuseRecibo.campos_desde_xml(
            parseada,
        )

    @classmethod
    def _procesar_acuse_recibo(
        cls,
        factura,
    ):

        if factura is None:

            return factura

        if not getattr(
            factura,
            "requiere_acuse_recibo",
            False,
        ):

            return factura

        from aplicacion.integraciones.dian.servicio_acuse_recibo import (
            ServicioAcuseRecibo,
        )

        ServicioAcuseRecibo.procesar(
            factura.id,
        )

        return cls.obtener_completa(
            factura.id,
        )

    @classmethod
    def preparar_desde_xml(
        cls,
        ruta_xml: str | Path,
    ) -> dict:

        parseada = parsear_factura_xml(
            ruta_xml,
        )

        if (
            parseada.cufe
            and cls.repositorio.existe_cufe(
                parseada.cufe,
            )
        ):

            existente = cls.repositorio.obtener_por_cufe(
                parseada.cufe,
            )

            raise ValueError(
                f"El CUFE ya está registrado en la factura "
                f"{existente.numero}.",
            )

        proveedor = cls.asegurar_proveedor(
            parseada.nit_proveedor,
            parseada.razon_social_proveedor,
        )

        from aplicacion.modulos.cartera.utilidades import (
            calcular_fecha_vencimiento,
        )

        fecha_vencimiento = calcular_fecha_vencimiento(
            parseada.fecha or date.today(),
            (
                proveedor.dias_credito
                if proveedor
                else 0
            ),
            fecha_vencimiento=parseada.fecha_vencimiento,
        )

        lineas = cls._lineas_desde_xml(
            parseada,
        )

        cabecera_base = {
            "numero": cls.generar_numero(),
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
            "es_credito": parseada.es_credito,
            "fecha_vencimiento": fecha_vencimiento,
            "origen": "xml",
            "ruta_xml": "",
            "estado": "recibida",
            "observaciones": "",
            "activo": True,
            **cls._campos_acuse_desde_xml(
                parseada,
            ),
        }

        if proveedor:
            cabecera_base["retefuente_id"] = (
                proveedor.retefuente_id
            )
            cabecera_base["reteica_id"] = (
                proveedor.reteica_id
            )
            cabecera_base["reteiva_id"] = (
                proveedor.reteiva_id
            )

        return {
            "cabecera": cabecera_base,
            "lineas": lineas,
            "ruta_xml_origen": parseada.ruta_xml_origen,
        }

    @classmethod
    def guardar_completa(
        cls,
        cabecera,
        lineas,
        id_registro=None,
    ):

        cabecera = cls.validar_cabecera(
            cabecera,
            id_registro,
        )

        lineas = cls.validar_lineas(
            lineas,
        )

        cls._aplicar_resumen(
            cabecera,
            lineas,
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
    def importar_desde_xml(
        cls,
        ruta_xml: str | Path,
    ):

        datos = cls.preparar_desde_xml(
            ruta_xml,
        )

        ruta_almacen = copiar_xml_almacen(
            datos["ruta_xml_origen"],
            carpeta_destino=cls.carpeta_xml(),
            cufe=datos["cabecera"].get(
                "cufe",
                "",
            ),
        )

        datos["cabecera"]["ruta_xml"] = ruta_almacen

        factura = cls.guardar_completa(
            datos["cabecera"],
            datos["lineas"],
        )

        return cls._procesar_acuse_recibo(
            factura,
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
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )
