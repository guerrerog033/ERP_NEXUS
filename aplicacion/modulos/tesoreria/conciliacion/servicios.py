from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

from aplicacion.base_datos.conexion import SessionLocal

from .modelos import ConciliacionBancaria, ExtractoBancario


class ServicioConciliacionBancaria:
    """Importación de extractos y conciliación automática."""

    @classmethod
    def importar_csv(
        cls,
        ruta: str | Path,
        *,
        banco: str = "Banco",
        cuenta: str = "000000",
    ) -> int:
        ruta = Path(ruta)
        importados = 0
        db = SessionLocal()

        try:
            with ruta.open(
                encoding="utf-8-sig",
                newline="",
            ) as archivo:
                lector = csv.DictReader(
                    archivo,
                )

                for fila in lector:
                    fecha = cls._parsear_fecha(
                        fila.get("fecha")
                        or fila.get("Fecha")
                        or "",
                    )

                    valor = cls._parsear_valor(
                        fila.get("valor")
                        or fila.get("Valor")
                        or fila.get("monto")
                        or "0",
                    )

                    if fecha is None or valor == 0:
                        continue

                    tipo = (
                        "credito"
                        if valor > 0
                        else "debito"
                    )

                    registro = ExtractoBancario(
                        banco=banco,
                        cuenta=cuenta,
                        fecha=fecha,
                        descripcion=str(
                            fila.get("descripcion")
                            or fila.get("Descripcion")
                            or "",
                        )[:250],
                        referencia=str(
                            fila.get("referencia")
                            or fila.get("Referencia")
                            or "",
                        )[:80],
                        valor=abs(valor),
                        tipo=tipo,
                        saldo=cls._parsear_valor(
                            fila.get("saldo")
                            or "0",
                        )
                        or None,
                        origen="csv",
                    )

                    db.add(registro)
                    importados += 1

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        if importados:
            cls.conciliar_automatico()

        return importados

    @classmethod
    def conciliar_automatico(cls) -> dict[str, int]:
        db = SessionLocal()
        conciliados = 0
        pendientes = 0

        try:
            extractos = (
                db.query(ExtractoBancario)
                .filter(
                    ExtractoBancario.conciliado.is_(False),
                )
                .all()
            )

            for extracto in extractos:
                match = cls._buscar_documento(
                    db,
                    extracto,
                )

                if match is None:
                    pendientes += 1
                    continue

                tipo_doc, doc_id = match

                db.add(
                    ConciliacionBancaria(
                        extracto_id=extracto.id,
                        tipo_documento=tipo_doc,
                        documento_id=doc_id,
                        valor=extracto.valor,
                    )
                )

                extracto.conciliado = True
                conciliados += 1

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        return {
            "conciliados": conciliados,
            "pendientes": pendientes,
        }

    @classmethod
    def _buscar_documento(
        cls,
        db,
        extracto: ExtractoBancario,
    ) -> tuple[str, int] | None:
        from aplicacion.modulos.tesoreria.comprobantes_egreso.modelos import (
            ComprobanteEgreso,
        )
        from aplicacion.modulos.tesoreria.recibos_caja.modelos import (
            ReciboCaja,
        )
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        referencia = str(
            extracto.referencia or "",
        ).upper()

        descripcion = str(
            extracto.descripcion or "",
        ).upper()

        if extracto.tipo == "debito":
            egresos = (
                db.query(ComprobanteEgreso)
                .filter(
                    ComprobanteEgreso.activo.is_(True),
                )
                .all()
            )

            for egreso in egresos:
                if cls._coincide_valor(
                    extracto.valor,
                    float(
                        egreso.valor_total or 0,
                    ),
                ) and cls._coincide_texto(
                    referencia,
                    descripcion,
                    egreso.numero,
                ):
                    return (
                        "comprobante_egreso",
                        egreso.id,
                    )

            facturas = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.estado_pago
                    == "pendiente",
                )
                .all()
            )

            for factura in facturas:
                if cls._coincide_valor(
                    extracto.valor,
                    float(
                        factura.saldo_pendiente
                        or factura.total
                        or 0,
                    ),
                ):
                    return (
                        "factura_compra",
                        factura.id,
                    )

        else:
            recibos = (
                db.query(ReciboCaja)
                .filter(
                    ReciboCaja.activo.is_(True),
                )
                .all()
            )

            for recibo in recibos:
                if cls._coincide_valor(
                    extracto.valor,
                    float(
                        recibo.valor_total or 0,
                    ),
                ) and cls._coincide_texto(
                    referencia,
                    descripcion,
                    recibo.numero,
                ):
                    return (
                        "recibo_caja",
                        recibo.id,
                    )

            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.estado_pago
                    == "pendiente",
                )
                .all()
            )

            for factura in facturas:
                if cls._coincide_valor(
                    extracto.valor,
                    float(
                        factura.saldo_pendiente
                        or factura.total
                        or 0,
                    ),
                ):
                    return (
                        "factura_venta",
                        factura.id,
                    )

        return None

    @classmethod
    def _coincide_valor(
        cls,
        valor_a: float,
        valor_b: float,
    ) -> bool:
        return abs(
            float(valor_a or 0)
            - float(valor_b or 0),
        ) < 1.0

    @classmethod
    def _coincide_texto(
        cls,
        referencia: str,
        descripcion: str,
        numero: str,
    ) -> bool:
        numero = str(
            numero or "",
        ).upper()

        if not numero:
            return True

        return (
            numero in referencia
            or numero in descripcion
        )

    @classmethod
    def _parsear_fecha(cls, texto: str):
        texto = str(texto or "").strip()

        for formato in (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ):
            try:
                return datetime.strptime(
                    texto,
                    formato,
                ).date()

            except ValueError:
                continue

        return None

    @classmethod
    def _parsear_valor(cls, texto: str) -> float:
        texto = str(
            texto or "0",
        ).strip()

        texto = re.sub(
            r"[^\d,.-]",
            "",
            texto,
        ).replace(
            ",",
            "",
        )

        try:
            return float(texto or 0)

        except ValueError:
            return 0.0

    @classmethod
    def listar_extractos(cls) -> list[ExtractoBancario]:
        db = SessionLocal()

        try:
            return (
                db.query(ExtractoBancario)
                .order_by(
                    ExtractoBancario.fecha.desc(),
                )
                .all()
            )

        finally:
            db.close()

    @classmethod
    def resumen(cls) -> dict[str, int]:
        db = SessionLocal()

        try:
            total = (
                db.query(ExtractoBancario)
                .count()
            )

            conciliados = (
                db.query(ExtractoBancario)
                .filter(
                    ExtractoBancario.conciliado.is_(True),
                )
                .count()
            )

            return {
                "total": total,
                "conciliados": conciliados,
                "pendientes": total - conciliados,
            }

        finally:
            db.close()
