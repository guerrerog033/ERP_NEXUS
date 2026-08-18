from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.nucleo.configuracion import Configuracion

from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)

from .repositorio import RepositorioCotizacion


class ServicioCotizacion(ServicioBase):

    repositorio = RepositorioCotizacion

    entidad_auditoria = "Cotizacion"

    modulo_auditoria = "ventas/cotizaciones"

    auditoria_campos_cabecera_excluir = [
        "fecha_creacion",
        "fecha_actualizacion",
    ]

    PREFIJO = "COT"

    LONGITUD = 6

    @classmethod
    def generar_numero(cls) -> str:

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        return ServicioNumeracion.siguiente_numero(
            "cotizacion_venta",
            cls.PREFIJO,
            longitud=cls.LONGITUD,
            consecutivo_minimo=(
                cls.repositorio.siguiente_secuencia(
                    cls.PREFIJO,
                )
                - 1
            ),
        )

    @classmethod
    def exigir_aprobada(
        cls,
        cotizacion,
    ) -> None:

        if (
            cotizacion is not None
            and str(
                cotizacion.estado or "",
            ).lower()
            == "borrador"
        ):

            raise ValueError(
                "Confirme la cotización antes de continuar.",
            )

    @classmethod
    def formato_predeterminado(cls) -> str:

        from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
            normalizar_formato_codigo,
        )

        return normalizar_formato_codigo(
            Configuracion.obtener(
                "impresion",
                "formato_predeterminado",
            ),
        )

    @classmethod
    def formatos_disponibles(cls) -> list[str]:

        formatos = Configuracion.obtener(
            "impresion",
            "formatos_disponibles",
        )

        from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
            normalizar_formato_codigo,
        )

        if isinstance(
            formatos,
            list,
        ) and formatos:

            return [
                normalizar_formato_codigo(
                    codigo,
                )
                for codigo in formatos
            ]

        return [
            "estandar",
            "carta",
            "corporativo",
            "moderno",
            "compacto",
            "tirilla",
        ]

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
    def _calcular_resumen(
        cls,
        lineas: list[dict],
        retefuente_id=None,
        reteica_id=None,
        reteiva_id=None,
    ) -> dict:

        subtotal = 0.0

        total_con_iva = 0.0

        for linea in lineas:

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

            subtotal_linea, total_linea = cls._calcular_linea(
                cantidad,
                precio,
                linea.get(
                    "impuesto_id",
                ),
                linea.get(
                    "precio_incluye_iva",
                    False,
                ),
            )

            descuento_pct = float(
                linea.get(
                    "descuento_porcentaje",
                    0,
                )
                or 0,
            )

            descuento_val = float(
                linea.get(
                    "descuento_valor",
                    0,
                )
                or 0,
            )

            if descuento_pct > 0:
                descuento_val = subtotal_linea * (
                    descuento_pct / 100
                )

            if descuento_val > 0:
                factor = max(
                    1 - (
                        descuento_val
                        / subtotal_linea
                    ),
                    0,
                ) if subtotal_linea else 1

                subtotal_linea = round(
                    subtotal_linea * factor,
                    2,
                )

                total_linea = round(
                    total_linea * factor,
                    2,
                )

            linea["total_linea"] = total_linea

            subtotal += subtotal_linea

            total_con_iva += total_linea

        valor_retefuente = round(
            subtotal
            * cls._porcentaje_impuesto(
                retefuente_id,
            )
            / 100,
            2,
        )

        valor_reteica = round(
            subtotal
            * cls._porcentaje_impuesto(
                reteica_id,
            )
            / 100,
            2,
        )

        iva_total = round(
            total_con_iva
            - subtotal,
            2,
        )

        valor_reteiva = round(
            iva_total
            * cls._porcentaje_impuesto(
                reteiva_id,
            )
            / 100,
            2,
        )

        total = round(
            total_con_iva
            - valor_retefuente
            - valor_reteica
            - valor_reteiva,
            2,
        )

        return {
            "subtotal": round(
                subtotal,
                2,
            ),
            "iva": iva_total,
            "retefuente": valor_retefuente,
            "reteica": valor_reteica,
            "reteiva": valor_reteiva,
            "total": total,
        }

    @classmethod
    def _subtotal_linea(
        cls,
        cantidad: float,
        precio: float,
        impuesto_id=None,
        precio_incluye_iva=False,
    ) -> float:

        return cls._calcular_linea(
            cantidad,
            precio,
            impuesto_id,
            precio_incluye_iva,
        )[0]

    @classmethod
    def _total_linea(
        cls,
        cantidad: float,
        precio: float,
        impuesto_id=None,
        precio_incluye_iva=False,
    ) -> float:

        return cls._calcular_linea(
            cantidad,
            precio,
            impuesto_id,
            precio_incluye_iva,
        )[1]

    @classmethod
    def _calcular_totales(
        cls,
        lineas: list[dict],
        retefuente_id=None,
        reteica_id=None,
        reteiva_id=None,
    ) -> tuple[float, float]:

        resumen = cls._calcular_resumen(
            lineas,
            retefuente_id,
            reteica_id,
            reteiva_id,
        )

        return (
            resumen["subtotal"],
            resumen["total"],
        )

    @classmethod
    def validar_lineas(
        cls,
        lineas,
    ):

        if not lineas:

            raise ValueError(
                "Agregue al menos una línea a la cotización.",
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
                }
            )

        if not lineas_validas:

            raise ValueError(
                "Las líneas deben tener producto, cantidad y precio válidos.",
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
                "El número de cotización es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una cotización con ese número.",
            )

        cliente_id = cabecera.get(
            "cliente_id",
        )

        if not cliente_id:

            raise ValueError(
                "Seleccione un cliente.",
            )

        from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
            normalizar_formato_codigo,
        )

        formato = normalizar_formato_codigo(
            cabecera.get(
                "formato_impresion",
                cls.formato_predeterminado(),
            ),
        )

        if formato not in cls.formatos_disponibles():

            formato = cls.formato_predeterminado()

        fecha = cabecera.get(
            "fecha",
        )

        if fecha is None:

            fecha = date.today()

        cabecera["numero"] = numero
        cabecera["cliente_id"] = int(
            cliente_id,
        )
        cabecera["formato_impresion"] = formato
        cabecera["fecha"] = fecha
        cabecera["observaciones"] = str(
            cabecera.get(
                "observaciones",
                "",
            )
            or "",
        ).strip()
        cabecera["vendedor"] = str(
            cabecera.get(
                "vendedor",
                "",
            )
            or "",
        ).strip()
        cabecera["estado"] = str(
            cabecera.get(
                "estado",
                "borrador",
            )
            or "borrador",
        )
        cabecera["activo"] = bool(
            cabecera.get(
                "activo",
                True,
            )
        )

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

        subtotal, total = cls._calcular_totales(
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

        cabecera["subtotal"] = subtotal
        cabecera["total"] = total

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

    @classmethod
    def _asegurar_codigo_aceptacion(
        cls,
        cotizacion,
    ) -> str:
        if getattr(
            cotizacion,
            "codigo_aceptacion",
            None,
        ):
            return cotizacion.codigo_aceptacion

        from aplicacion.api.servidor import (
            ServidorApiErp,
        )

        codigo = ServidorApiErp.generar_codigo_verificacion()

        cls.repositorio.actualizar_campos(
            cotizacion.id,
            {
                "codigo_aceptacion": codigo,
                "codigo_verificacion": (
                    ServidorApiErp
                    .generar_codigo_verificacion()
                ),
            },
        )

        return codigo

    @classmethod
    def obtener_por_codigo_aceptacion(
        cls,
        codigo: str,
    ):
        return cls.repositorio.obtener_por_codigo_aceptacion(
            codigo,
        )

    @classmethod
    def aceptar_por_codigo(
        cls,
        codigo: str,
        *,
        codigo_verificacion: str = "",
        firma_cliente: str = "",
    ) -> dict:
        cotizacion = cls.obtener_por_codigo_aceptacion(
            codigo,
        )

        if cotizacion is None:
            return {
                "exito": False,
                "mensaje": "Cotización no encontrada.",
            }

        esperado = str(
            getattr(
                cotizacion,
                "codigo_verificacion",
                "",
            )
            or "",
        )

        if (
            esperado
            and codigo_verificacion.upper()
            != esperado.upper()
        ):
            return {
                "exito": False,
                "mensaje": "Código de verificación inválido.",
            }

        cls.repositorio.actualizar_campos(
            cotizacion.id,
            {
                "estado_aceptacion": "aceptada",
                "firma_cliente": firma_cliente,
                "estado": "aprobada",
            },
        )

        return {
            "exito": True,
            "mensaje": "Cotización aceptada.",
            "numero": cotizacion.numero,
        }

    @classmethod
    def preparar_aceptacion(
        cls,
        id_registro: int,
    ) -> dict:
        cotizacion = cls.obtener_completa(
            id_registro,
        )

        if cotizacion is None:
            raise ValueError(
                "Cotización no encontrada.",
            )

        codigo = cls._asegurar_codigo_aceptacion(
            cotizacion,
        )

        puerto = Configuracion.obtener(
            "api",
            "puerto",
            8765,
        )

        url = (
            f"http://127.0.0.1:{puerto}"
            f"/portal/cotizacion/{codigo}"
        )

        return {
            "codigo": codigo,
            "url": url,
            "codigo_verificacion": (
                getattr(
                    cotizacion,
                    "codigo_verificacion",
                    "",
                )
            ),
        }
