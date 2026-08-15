from __future__ import annotations


def importar_modelos() -> None:
    """
    Registra todos los modelos ORM en ``Base.metadata``.

    Usado por ``startup.inicializar_sistema`` y ``alembic/env.py``.
    """

    from aplicacion.maestros.categorias.modelos import (  # noqa: F401
        Categoria,
    )

    from aplicacion.maestros.marcas.modelos import (  # noqa: F401
        Marca,
    )

    from aplicacion.maestros.productos.modelos import (  # noqa: F401
        CatalogoVariante,
        Producto,
        ProductoPrecio,
        ProductoVariante,
    )

    from aplicacion.maestros.impuestos.modelos import (  # noqa: F401
        Impuesto,
    )

    from aplicacion.maestros.listas_precio.modelos import (  # noqa: F401
        ListaPrecio,
    )

    from aplicacion.modulos.ventas.cotizaciones.modelos import (  # noqa: F401
        Cotizacion,
        CotizacionDetalle,
    )

    from aplicacion.modulos.ventas.proformas.modelos import (  # noqa: F401
        Proforma,
        ProformaDetalle,
    )

    from aplicacion.modulos.ventas.pedidos.modelos import (  # noqa: F401
        OrdenPedido,
        OrdenPedidoDetalle,
        PedidoReserva,
    )

    from aplicacion.modulos.compras.facturas.modelos import (  # noqa: F401
        FacturaCompra,
        FacturaCompraDetalle,
        FacturaCompraEventoRadian,
    )

    from aplicacion.modulos.compras.notas_credito.modelos import (  # noqa: F401
        NotaCreditoCompra,
        NotaCreditoCompraDetalle,
    )

    from aplicacion.modulos.compras.ordenes.modelos import (  # noqa: F401
        OrdenCompra,
        OrdenCompraDetalle,
        RecepcionCompra,
        RecepcionCompraDetalle,
    )

    from aplicacion.modulos.contabilidad.modelos import (  # noqa: F401
        PlanCuenta,
        AsientoContable,
        AsientoDetalle,
        ReglaContabilizacion,
    )

    from aplicacion.modulos.inventario.modelos import (  # noqa: F401
        Bodega,
        ExistenciaBodega,
        MovimientoInventario,
    )

    from aplicacion.modulos.ventas.facturas.modelos import (  # noqa: F401
        FacturaVenta,
        FacturaVentaDetalle,
    )

    from aplicacion.modulos.ventas.notas_credito.modelos import (  # noqa: F401
        NotaCreditoVenta,
        NotaCreditoVentaDetalle,
    )

    from aplicacion.modulos.ventas.notas_debito.modelos import (  # noqa: F401
        NotaDebitoVenta,
        NotaDebitoVentaDetalle,
    )

    from aplicacion.modulos.compras.documentos_soporte.modelos import (  # noqa: F401
        DocumentoSoporte,
        DocumentoSoporteDetalle,
    )

    from aplicacion.modulos.ventas.remisiones.modelos import (  # noqa: F401
        RemisionVenta,
        RemisionVentaDetalle,
    )

    from aplicacion.modulos.ventas.guias_remision.modelos import (  # noqa: F401
        GuiaRemisionElectronica,
        GuiaRemisionElectronicaDetalle,
    )

    from aplicacion.autenticacion.modelos import (  # noqa: F401
        Rol,
        Usuario,
    )

    from aplicacion.seguridad.modelos import (  # noqa: F401
        AuditoriaCampo,
        AuditoriaEvento,
    )

    from aplicacion.licencias.modelos import (  # noqa: F401
        LicenciaActivacion,
        SerialLicencia,
    )

    from aplicacion.modulos.tesoreria.recibos_caja.modelos import (  # noqa: F401
        ReciboCaja,
        ReciboCajaDetalle,
    )

    from aplicacion.modulos.tesoreria.comprobantes_egreso.modelos import (  # noqa: F401
        ComprobanteEgreso,
        ComprobanteEgresoDetalle,
    )

    from aplicacion.maestros.terceros.modelos import (  # noqa: F401
        PerfilCliente,
        PerfilProveedor,
        Tercero,
        TerceroContacto,
        TerceroCuentaBancaria,
        TerceroDireccion,
    )

    from aplicacion.maestros.empresas.modelos import (  # noqa: F401
        Empresa,
        EmpresaBanco,
    )

    from aplicacion.maestros.unidades_medida.modelos import (  # noqa: F401
        UnidadMedida,
    )

    from aplicacion.maestros.formas_pago.modelos import (  # noqa: F401
        FormaPago,
    )

    from aplicacion.maestros.medios_pago.modelos import (  # noqa: F401
        MedioPago,
    )

    from aplicacion.maestros.vendedores.modelos import (  # noqa: F401
        Vendedor,
    )

    from aplicacion.maestros.atributos.modelos import (  # noqa: F401
        Atributo,
        ValorAtributo,
    )

    from aplicacion.nucleo.documentos.modelos import (  # noqa: F401
        DocumentoVinculo,
    )

    from aplicacion.nucleo.numeracion.modelos import (  # noqa: F401
        NumeracionDocumento,
    )

    from aplicacion.modulos.nomina.modelos import (  # noqa: F401
        ContratoEmpleado,
        Empleado,
        LiquidacionConcepto,
        LiquidacionNomina,
        NovedadNomina,
        PeriodoNomina,
        ProvisionPrestacion,
    )

    from aplicacion.modulos.crm.modelos import (  # noqa: F401
        ActividadCRM,
        OportunidadCRM,
    )

    from aplicacion.modulos.logistica.despacho.modelos import (  # noqa: F401
        DespachoEvidencia,
        DespachoPedido,
    )

    from aplicacion.modulos.ventas.pos.modelos import (  # noqa: F401
        PosCierreCaja,
        PosVentaLog,
    )

    from aplicacion.modulos.tesoreria.conciliacion.modelos import (  # noqa: F401
        ConciliacionBancaria,
        ExtractoBancario,
    )
