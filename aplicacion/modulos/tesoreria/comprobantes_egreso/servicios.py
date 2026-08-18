from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.modulos.compras.facturas.modelos import FacturaCompra
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioComprobanteEgreso


FORMAS_PAGO = (
    ("Transferencia", "transferencia"),
    ("Efectivo", "efectivo"),
    ("Cheque", "cheque"),
)


class ServicioComprobanteEgreso(ServicioBase):

    repositorio = RepositorioComprobanteEgreso

    PREFIJO = "CE"

    LONGITUD = 6

    @classmethod
    def _prefijo(cls) -> str:

        return str(
            Configuracion.obtener(
                "tesoreria",
                "prefijo_comprobante_egreso",
            )
            or cls.PREFIJO,
        )

    @classmethod
    def _longitud(cls) -> int:

        return int(
            Configuracion.obtener(
                "tesoreria",
                "longitud_secuencia",
            )
            or cls.LONGITUD,
        )

    @classmethod
    def generar_numero(cls) -> str:

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        prefijo = cls._prefijo()

        return ServicioNumeracion.siguiente_numero(
            "comprobante_egreso",
            prefijo,
            longitud=cls._longitud(),
            consecutivo_minimo=(
                cls.repositorio.siguiente_secuencia(prefijo) - 1
            ),
        )

    @classmethod
    def listar_facturas_pendientes(
        cls,
        proveedor_id: int,
    ) -> list[FacturaCompra]:

        return cls.repositorio.listar_facturas_pendientes(
            proveedor_id,
        )

    @classmethod
    def obtener_completo(
        cls,
        id_registro,
    ):

        return cls.repositorio.obtener_completo(
            id_registro,
        )

    @classmethod
    def _validar_lineas(
        cls,
        proveedor_id: int,
        lineas: list[dict],
    ) -> float:

        if not lineas:

            raise ValueError(
                "Seleccione al menos una factura a pagar.",
            )

        total = 0.0

        pendientes = {
            factura.id: factura
            for factura in cls.listar_facturas_pendientes(
                proveedor_id,
            )
        }

        for linea in lineas:

            factura_id = int(
                linea["factura_compra_id"],
            )

            valor = float(
                linea.get(
                    "valor_aplicado",
                    0,
                )
                or 0,
            )

            if valor <= 0:

                continue

            factura = pendientes.get(
                factura_id,
            )

            if factura is None:

                raise ValueError(
                    "Una de las facturas seleccionadas "
                    "no está pendiente de pago.",
                )

            saldo = float(
                factura.saldo_pendiente or 0,
            )

            if valor > saldo + 0.01:

                raise ValueError(
                    f"El valor aplicado a la factura "
                    f"{factura.numero} supera el saldo "
                    f"({saldo:,.2f}).",
                )

            total += valor

        if total <= 0:

            raise ValueError(
                "El valor total del egreso debe ser mayor a cero.",
            )

        return total

    @classmethod
    def _validar_anticipo(
        cls,
        cabecera: dict,
    ) -> float:

        total = float(
            cabecera.get(
                "valor_total",
                0,
            )
            or 0,
        )

        if total <= 0:

            raise ValueError(
                "Ingrese el valor del abono o anticipo.",
            )

        return total

    @classmethod
    def guardar_completo(
        cls,
        cabecera: dict,
        lineas: list[dict],
        *,
        id_registro=None,
    ):

        proveedor_id = int(
            cabecera["proveedor_id"],
        )

        es_anticipo = bool(
            cabecera.get(
                "es_anticipo",
            ),
        )

        if es_anticipo:

            total = cls._validar_anticipo(
                cabecera,
            )

            lineas_validas: list[dict] = []

        else:

            total = cls._validar_lineas(
                proveedor_id,
                lineas,
            )

            lineas_validas = [
                {
                    "factura_compra_id": int(
                        linea["factura_compra_id"],
                    ),
                    "valor_aplicado": float(
                        linea["valor_aplicado"],
                    ),
                }
                for linea in lineas
                if float(
                    linea.get(
                        "valor_aplicado",
                        0,
                    )
                    or 0,
                )
                > 0
            ]

        datos = dict(cabecera)

        datos.pop(
            "es_anticipo",
            None,
        )

        datos["valor_total"] = total

        if id_registro is None:

            datos.setdefault(
                "numero",
                cls.generar_numero(),
            )

            datos.setdefault(
                "prefijo",
                cls._prefijo(),
            )

            datos.setdefault(
                "fecha",
                date.today(),
            )

            datos.setdefault(
                "estado",
                "borrador",
            )

            datos.setdefault(
                "activo",
                True,
            )

        return cls.repositorio.guardar_completo(
            datos,
            lineas_validas,
            id_registro=id_registro,
        )
