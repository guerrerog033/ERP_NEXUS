from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioGuiaRemisionElectronica


class ServicioGuiaRemisionElectronica(ServicioBase):

    repositorio = RepositorioGuiaRemisionElectronica

    entidad_auditoria = "GuiaRemisionElectronica"

    modulo_auditoria = "ventas/guias_remision"

    PREFIJO = "GRE"

    LONGITUD = 6

    @classmethod
    def _prefijo(cls) -> str:

        return str(
            Configuracion.obtener(
                "ventas",
                "prefijo_guia_remision",
            )
            or Configuracion.obtener(
                "dian",
                "prefijo_guia_remision",
            )
            or cls.PREFIJO,
        )

    @classmethod
    def generar_numero(cls) -> str:

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        longitud = int(
            Configuracion.obtener(
                "ventas",
                "longitud_secuencia",
            )
            or cls.LONGITUD,
        )

        prefijo = cls._prefijo()

        return ServicioNumeracion.siguiente_numero(
            "guia_remision_venta",
            prefijo,
            longitud=longitud,
            consecutivo_minimo=(
                cls.repositorio.siguiente_secuencia(prefijo) - 1
            ),
        )

    @classmethod
    def obtener_completa(
        cls,
        id_registro: int,
    ):

        return cls.repositorio.obtener_completa(
            id_registro,
        )

    @classmethod
    def obtener_por_remision(
        cls,
        remision_id: int,
    ):

        return cls.repositorio.obtener_por_remision(
            remision_id,
        )

    @classmethod
    def crear_desde_remision(
        cls,
        remision_id: int,
        *,
        conductor: str = "",
        vehiculo: str = "",
        placa: str = "",
        transportadora: str = "",
    ):

        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )
        from aplicacion.modulos.ventas.remisiones.servicios import (
            ServicioRemision,
        )

        existente = cls.obtener_por_remision(
            remision_id,
        )

        if (
            existente is not None
            and existente.estado
            in (
                "borrador",
                "generada",
                "emitida",
            )
        ):

            raise ValueError(
                f"La remisión ya tiene la guía "
                f"electrónica {existente.numero}.",
            )

        remision = ServicioRemision.obtener_completa(
            remision_id,
        )

        if remision is None:

            raise ValueError(
                "No se encontró la remisión interna.",
            )

        if not remision.detalles:

            raise ValueError(
                "La remisión no tiene líneas.",
            )

        cliente = TerceroServicio.obtener_por_id(
            remision.cliente_id,
        )

        direccion_destino = ""
        ciudad_destino = ""
        departamento_destino = ""

        if cliente is not None:

            direccion_destino = (
                cliente.direccion or ""
            )

            ciudad_destino = (
                cliente.ciudad or ""
            )

            departamento_destino = (
                cliente.departamento or ""
            )

        cabecera = {
            "numero": cls.generar_numero(),
            "prefijo": cls._prefijo(),
            "fecha": date.today(),
            "remision_id": remision.id,
            "remision_numero": remision.numero,
            "cliente_id": remision.cliente_id,
            "subtotal": remision.subtotal,
            "total": remision.total,
            "direccion_origen": str(
                Configuracion.obtener(
                    "empresa",
                    "direccion",
                )
                or "",
            ),
            "ciudad_origen": str(
                Configuracion.obtener(
                    "empresa",
                    "ciudad",
                )
                or "",
            ),
            "departamento_origen": str(
                Configuracion.obtener(
                    "empresa",
                    "departamento",
                )
                or "",
            ),
            "direccion_destino": direccion_destino,
            "ciudad_destino": ciudad_destino,
            "departamento_destino": departamento_destino,
            "conductor": conductor,
            "vehiculo": vehiculo,
            "placa": placa,
            "transportadora": transportadora,
            "observaciones": (
                f"Guía electrónica de remisión interna "
                f"{remision.numero}"
            ),
            "estado": "borrador",
            "activo": True,
        }

        lineas = [
            {
                "producto_id": detalle.producto_id,
                "producto_variante_id": (
                    detalle.producto_variante_id
                ),
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": (
                    detalle.precio_unitario
                ),
                "total_linea": detalle.total_linea,
            }
            for detalle in remision.detalles
        ]

        return cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

    @classmethod
    def guia_emitida_para_remision(
        cls,
        remision_id: int,
    ) -> bool:

        guia = cls.obtener_por_remision(
            remision_id,
        )

        if guia is None:

            return False

        return guia.estado == "emitida"

    @classmethod
    def exigir_guia_emitida_logistica(cls) -> bool:

        valor = Configuracion.obtener(
            "ventas",
            "exigir_guia_emitida_entrega",
        )

        if valor is None:

            return True

        return bool(
            valor,
        )

    @classmethod
    def validar_guia_emitida_remision(
        cls,
        remision_id: int,
    ) -> None:

        if not cls.exigir_guia_emitida_logistica():

            return

        if cls.guia_emitida_para_remision(
            remision_id,
        ):

            return

        guia = cls.obtener_por_remision(
            remision_id,
        )

        if guia is None:

            raise ValueError(
                "Debe crear y emitir la guía de remisión "
                "electrónica antes de marcar entregado.",
            )

        raise ValueError(
            f"La guía {guia.numero} debe estar emitida "
            f"ante la DIAN (estado actual: {guia.estado}).",
        )
