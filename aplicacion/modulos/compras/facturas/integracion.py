from __future__ import annotations

from aplicacion.integraciones.dian.validador_cufe import (    ValidadorCufe,
)
from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioFacturaCompra
from .servicios import ServicioFacturaCompra


class IntegracionFacturaCompra:

    @classmethod
    def validar_cufe_online(
        cls,
        id_registro: int,
    ):

        factura = ServicioFacturaCompra.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if not factura.cufe:

            raise ValueError(
                "La factura no tiene CUFE.",
            )

        resultado = ValidadorCufe.validar(
            factura.cufe,
        )

        if resultado.error and not resultado.valido:

            raise ValueError(
                resultado.error,
            )

        RepositorioFacturaCompra.actualizar_validacion_cufe(
            id_registro,
            valido=resultado.valido,
            estado=resultado.estado,
            mensaje=resultado.mensaje,
        )

        if (
            resultado.valido
            and factura.estado == "recibida"
        ):

            RepositorioFacturaCompra.actualizar_estado(
                id_registro,
                "validada",
            )

        return resultado

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        factura = ServicioFacturaCompra.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.estado == "contabilizada":

            raise ValueError(
                "La factura ya está contabilizada.",
            )

        if factura.estado == "pendiente_revision":

            raise ValueError(
                "Apruebe la revisión de la factura "
                "antes de contabilizar.",
            )

        from aplicacion.modulos.compras.integracion_oc import (
            ServicioIntegracionCompras,
        )

        ServicioIntegracionCompras.validar_contabilizacion(
            factura,
        )

        if (
            factura.cufe
            and Configuracion.obtener(
                "compras",
                "exigir_cufe_validado_contabilizar",
            )
            and not factura.cufe_validado
        ):

            raise ValueError(
                "Valide el CUFE en DIAN antes "
                "de contabilizar.",
            )

        ServicioContabilidad.inicializar_plan()
        ServicioInventario.inicializar_bodega()

        movimientos = (
            ServicioInventario.registrar_entrada_factura_compra(
                factura,
            )
        )

        asiento = ServicioContabilidad.registrar_factura_compra(
            factura,
        )

        RepositorioFacturaCompra.actualizar_contabilizacion(
            id_registro,
            asiento_id=asiento.id,
        )

        inventario_aplicado = bool(
            movimientos,
        )

        if (
            not inventario_aplicado
            and ServicioIntegracionCompras.inventario_en_recepcion()
            and factura.orden_compra_id
        ):

            inventario_aplicado = True

        RepositorioFacturaCompra.actualizar_inventario_aplicado(
            id_registro,
            valor=inventario_aplicado,
        )

        return asiento

    @classmethod
    def aprobar_revision(
        cls,
        id_registro: int,
    ):

        factura = ServicioFacturaCompra.obtener_completa(
            id_registro,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        if factura.estado != "pendiente_revision":

            raise ValueError(
                "La factura no está pendiente de revisión.",
            )

        nuevo_estado = (
            "validada"
            if factura.cufe_validado
            else "recibida"
        )

        RepositorioFacturaCompra.actualizar_estado(
            id_registro,
            nuevo_estado,
        )

        from .automatizacion import (
            ServicioAutomatizacionCompras,
        )

        ServicioAutomatizacionCompras.contabilizar_automatico(
            id_registro,
        )

        return nuevo_estado

    @classmethod
    def generar_acuse_recibo(
        cls,
        id_registro: int,
        *,
        forzar: bool = False,
    ):

        from aplicacion.integraciones.dian.servicio_acuse_recibo import (
            ServicioAcuseRecibo,
        )

        return ServicioAcuseRecibo.procesar(
            id_registro,
            forzar=forzar,
        )
