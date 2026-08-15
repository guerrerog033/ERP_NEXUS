from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.modulos.ventas.facturas.servicios import (
    ServicioFacturaVenta,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioNotaDebitoVenta


MOTIVOS_NOTA_DEBITO = (
    "Intereses por mora",
    "Ajuste de precio al alza",
    "Cargos adicionales",
    "Corrección de valor",
    "Otros",
)


class ServicioNotaDebitoVenta(ServicioBase):

    repositorio = RepositorioNotaDebitoVenta

    entidad_auditoria = "NotaDebitoVenta"

    modulo_auditoria = "ventas/notas_debito"

    PREFIJO = "ND"

    LONGITUD = 6

    @classmethod
    def _prefijo(cls) -> str:

        return str(
            Configuracion.obtener(
                "ventas",
                "prefijo_nota_debito",
            )
            or cls.PREFIJO,
        )

    @classmethod
    def _longitud(cls) -> int:

        try:

            return int(
                Configuracion.obtener(
                    "ventas",
                    "longitud_secuencia_nd",
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
    def listar_facturas_emitidas(
        cls,
        limite: int = 50,
    ):

        return cls.repositorio.listar_facturas_emitidas(
            limite,
        )

    @classmethod
    def crear_desde_factura(
        cls,
        factura_id: int,
        motivo: str | None = None,
    ):

        factura = ServicioFacturaVenta.obtener_completa(
            factura_id,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.estado not in (
            "emitida",
            "generada",
            "contabilizada",
        ):

            raise ValueError(
                "La factura debe estar emitida "
                "o confirmada.",
            )

        lineas = [
            {
                "producto_id": None,
                "producto_variante_id": None,
                "descripcion": (
                    "Cargo adicional / ajuste"
                ),
                "cantidad": 1,
                "precio_unitario": 0,
                "impuesto_id": None,
                "precio_incluye_iva": False,
                "total_linea": 0,
            },
        ]

        cabecera = {
            "numero": cls.generar_numero(),
            "prefijo": Configuracion.obtener(
                "dian",
                "prefijo_nota_debito",
            )
            or "ND",
            "consecutivo_dian": str(
                cls.repositorio.siguiente_secuencia(
                    cls._prefijo(),
                ),
            ),
            "fecha": date.today(),
            "cliente_id": factura.cliente_id,
            "factura_id": factura.id,
            "motivo": (
                motivo
                or MOTIVOS_NOTA_DEBITO[0]
            ),
            "factura_cufe": factura.cufe,
            "retefuente_id": getattr(
                factura,
                "retefuente_id",
                None,
            ),
            "reteica_id": getattr(
                factura,
                "reteica_id",
                None,
            ),
            "reteiva_id": getattr(
                factura,
                "reteiva_id",
                None,
            ),
            "observaciones": (
                f"Referencia factura {factura.numero}"
            ),
            "estado": "borrador",
            "activo": True,
        }

        ServicioFacturaVenta._aplicar_resumen(
            cabecera,
            lineas,
        )

        return cls.repositorio.guardar_completa(
            cabecera,
            lineas,
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
                "El número de nota débito es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una nota débito con ese número.",
            )

        if not cabecera.get(
            "cliente_id",
        ):

            raise ValueError(
                "Seleccione un cliente.",
            )

        if not cabecera.get(
            "factura_id",
        ):

            raise ValueError(
                "La nota débito debe referenciar "
                "una factura.",
            )

        cabecera["numero"] = numero

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

        lineas = ServicioFacturaVenta.validar_lineas(
            lineas,
        )

        ServicioFacturaVenta._aplicar_resumen(
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
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )
