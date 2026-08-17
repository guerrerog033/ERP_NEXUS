from __future__ import annotations

from datetime import date


class ServicioPortalEmpleado:
    """
    Consultas de solo lectura para el portal móvil de empleados:
    inventario, cartera y ventas del día. Reutiliza los mismos
    servicios que ya usa el escritorio — este módulo solo adapta
    el resultado para las vistas HTML del portal.
    """

    @classmethod
    def resumen_cartera(cls) -> dict:

        from aplicacion.modulos.cartera.servicios import (
            ServicioCartera,
        )

        resumen = ServicioCartera.resumen()

        vencidas = ServicioCartera.listar_cxc(
            solo_vencidos=True,
        )

        vencidas_ordenadas = sorted(
            vencidas,
            key=lambda fila: fila["saldo"],
            reverse=True,
        )[:15]

        resumen["clientes_vencidos"] = vencidas_ordenadas

        return resumen

    @classmethod
    def ventas_del_dia(cls) -> dict:

        from aplicacion.modulos.reportes.servicios import (
            ServicioReportes,
        )

        hoy = date.today()

        filas = ServicioReportes.ventas_por_periodo(
            fecha_desde=hoy,
            fecha_hasta=hoy,
        )

        total = sum(
            float(fila.get("total", 0) or 0)
            for fila in filas
        )

        return {
            "fecha": hoy,
            "facturas": filas,
            "total": total,
            "cantidad": len(filas),
        }

    @classmethod
    def buscar_inventario(
        cls,
        texto: str,
    ) -> list[dict]:

        from aplicacion.maestros.productos.repositorio import (
            RepositorioProducto,
        )

        texto = (texto or "").strip()

        if not texto:

            return []

        productos = RepositorioProducto.buscar(
            texto,
        )[:30]

        return [
            {
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "existencia": float(
                    producto.existencia or 0,
                ),
                "stock_minimo": float(
                    producto.stock_minimo or 0,
                ),
            }
            for producto in productos
        ]
