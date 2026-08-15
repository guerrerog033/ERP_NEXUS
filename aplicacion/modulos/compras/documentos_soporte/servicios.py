from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)
from aplicacion.maestros.terceros.repositorio import (
    TerceroRepositorio,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioDocumentoSoporte


class ServicioDocumentoSoporte(ServicioBase):

    repositorio = RepositorioDocumentoSoporte

    entidad_auditoria = "DocumentoSoporte"

    modulo_auditoria = "compras/documentos_soporte"

    PREFIJO = "DS"

    LONGITUD = 6

    @classmethod
    def generar_numero(cls) -> str:

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        prefijo = str(
            Configuracion.obtener(
                "compras",
                "prefijo_documento_soporte",
            )
            or cls.PREFIJO,
        )

        return ServicioNumeracion.siguiente_numero(
            "documento_soporte_compra",
            prefijo,
            longitud=cls.LONGITUD,
        )

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
            impuesto.porcentaje or 0,
        )

    @classmethod
    def _calcular_linea(
        cls,
        cantidad: float,
        precio: float,
        impuesto_id=None,
    ) -> tuple[float, float]:

        bruto = float(
            cantidad or 0,
        ) * float(
            precio or 0,
        )

        porcentaje = cls._porcentaje_impuesto(
            impuesto_id,
        )

        iva = bruto * porcentaje / 100

        return bruto, bruto + iva

    @classmethod
    def _aplicar_resumen(
        cls,
        cabecera: dict,
        lineas: list[dict],
    ) -> None:

        subtotal = 0.0
        iva = 0.0

        for linea in lineas:

            bruto, total_linea = cls._calcular_linea(
                linea.get(
                    "cantidad",
                    0,
                ),
                linea.get(
                    "precio_unitario",
                    0,
                ),
                linea.get(
                    "impuesto_id",
                ),
            )

            linea["total_linea"] = total_linea
            subtotal += bruto
            iva += total_linea - bruto

        cabecera["subtotal"] = subtotal
        cabecera["iva"] = iva
        cabecera["total"] = subtotal + iva

    @classmethod
    def validar_lineas(
        cls,
        lineas: list[dict],
    ) -> list[dict]:

        if not lineas:

            raise ValueError(
                "Agregue al menos una línea.",
            )

        resultado = []

        for linea in lineas:

            descripcion = str(
                linea.get(
                    "descripcion",
                    "",
                )
                or "",
            ).strip()

            if not descripcion:

                raise ValueError(
                    "Cada línea debe tener descripción.",
                )

            cantidad = float(
                linea.get(
                    "cantidad",
                    0,
                )
                or 0,
            )

            if cantidad <= 0:

                raise ValueError(
                    "La cantidad debe ser mayor a cero.",
                )

            resultado.append(
                {
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "precio_unitario": float(
                        linea.get(
                            "precio_unitario",
                            0,
                        )
                        or 0,
                    ),
                    "impuesto_id": linea.get(
                        "impuesto_id",
                    ),
                    "total_linea": float(
                        linea.get(
                            "total_linea",
                            0,
                        )
                        or 0,
                    ),
                }
            )

        return resultado

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
                "El número del documento es obligatorio.",
            )

        if cls.repositorio.existe_numero(
            numero,
            id_registro,
        ):

            raise ValueError(
                "Ya existe un documento con ese número.",
            )

        proveedor_id = cabecera.get(
            "proveedor_id",
        )

        if not proveedor_id:

            raise ValueError(
                "Seleccione un proveedor.",
            )

        proveedor = TerceroRepositorio.obtener_por_id(
            proveedor_id,
        )

        if proveedor is None:

            raise ValueError(
                "No se encontró el proveedor.",
            )

        cabecera["numero"] = numero
        cabecera["nit_proveedor"] = (
            proveedor.numero_documento
        )
        cabecera["razon_social_proveedor"] = (
            proveedor.razon_social
            or proveedor.nombre_completo
            or proveedor.nombre_comercial
            or ""
        )

        if not cabecera.get(
            "fecha",
        ):

            cabecera["fecha"] = date.today()

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
