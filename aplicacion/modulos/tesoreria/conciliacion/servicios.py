from __future__ import annotations

import csv
import re
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path

DIAS_VENTANA_MATCH_AVANZADO = 60

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
                matches = cls._buscar_documentos(
                    db,
                    extracto,
                )

                if not matches:
                    pendientes += 1
                    continue

                for tipo_doc, doc_id, valor_aplicado, estado in matches:

                    db.add(
                        ConciliacionBancaria(
                            extracto_id=extracto.id,
                            tipo_documento=tipo_doc,
                            documento_id=doc_id,
                            valor=valor_aplicado,
                            estado=estado,
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
    def _buscar_documentos(
        cls,
        db,
        extracto: ExtractoBancario,
    ) -> list[tuple[str, int, float, str]] | None:
        """
        Intenta, en orden: (1) el match exacto de un solo documento
        que ya maneja `_buscar_documento`, (2) una combinación de
        varias facturas pendientes cuya suma cuadra con el
        movimiento (pago único que cubre varias facturas), y (3) un
        pago parcial de una sola factura identificada por su número
        en la referencia/descripción del movimiento.
        """

        match_simple = cls._buscar_documento(
            db,
            extracto,
        )

        if match_simple is not None:

            tipo_doc, doc_id = match_simple

            return [
                (
                    tipo_doc,
                    doc_id,
                    float(extracto.valor or 0),
                    "conciliado",
                )
            ]

        combinacion = cls._buscar_combinacion_facturas(
            db,
            extracto,
        )

        if combinacion is not None:

            return combinacion

        parcial = cls._buscar_pago_parcial(
            db,
            extracto,
        )

        if parcial is not None:

            return [parcial]

        return None

    @classmethod
    def _facturas_pendientes_por_tipo(
        cls,
        db,
        extracto: ExtractoBancario,
    ):
        if extracto.tipo == "debito":
            from aplicacion.modulos.compras.facturas.modelos import (
                FacturaCompra,
            )

            return (
                "factura_compra",
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.estado_pago == "pendiente",
                )
                .all(),
            )

        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        return (
            "factura_venta",
            db.query(FacturaVenta)
            .filter(
                FacturaVenta.estado_pago == "pendiente",
            )
            .all(),
        )

    @classmethod
    def _filtrar_por_ventana_fecha(
        cls,
        facturas,
        extracto: ExtractoBancario,
    ):
        """
        Los matches combinado/parcial no exigen coincidencia de
        texto contra cada factura (o solo la exigen para una de
        varias, en el caso combinado), así que sin este filtro se
        arriesga a emparejar facturas pendientes viejas y sin
        relación cuya suma cuadra por pura coincidencia. Se limita
        la búsqueda a facturas emitidas dentro de una ventana
        razonable alrededor de la fecha del movimiento bancario.
        """

        if extracto.fecha is None:
            return facturas

        desde = extracto.fecha - timedelta(
            days=DIAS_VENTANA_MATCH_AVANZADO,
        )
        hasta = extracto.fecha + timedelta(
            days=DIAS_VENTANA_MATCH_AVANZADO,
        )

        return [
            factura
            for factura in facturas
            if factura.fecha is not None
            and desde <= factura.fecha <= hasta
        ]

    @classmethod
    def _buscar_combinacion_facturas(
        cls,
        db,
        extracto: ExtractoBancario,
        *,
        maximo_candidatos: int = 15,
        maximo_facturas: int = 4,
    ) -> list[tuple[str, int, float, str]] | None:
        """
        Busca un subconjunto de facturas pendientes DEL MISMO
        tercero cuya suma cuadre con el movimiento — el caso real
        es un cliente/proveedor que paga varias facturas suyas de
        una sola vez. Agrupar por tercero es la señal que evita
        emparejar facturas de terceros distintos cuya suma coincide
        por pura casualidad.
        """

        objetivo = float(extracto.valor or 0)

        if objetivo <= 0:
            return None

        tipo_doc, facturas = cls._facturas_pendientes_por_tipo(
            db,
            extracto,
        )

        facturas = cls._filtrar_por_ventana_fecha(
            facturas,
            extracto,
        )

        campo_tercero = (
            "proveedor_id"
            if extracto.tipo == "debito"
            else "cliente_id"
        )

        por_tercero: dict[int, list[tuple[int, float]]] = {}

        for factura in facturas:

            tercero_id = getattr(
                factura,
                campo_tercero,
                None,
            )

            if not tercero_id:
                continue

            saldo = float(
                factura.saldo_pendiente or factura.total or 0,
            )

            if not (0 < saldo < objetivo):
                continue

            por_tercero.setdefault(
                tercero_id,
                [],
            ).append(
                (factura.id, saldo),
            )

        for candidatos in por_tercero.values():

            candidatos.sort(
                key=lambda item: item[1],
                reverse=True,
            )
            candidatos = candidatos[:maximo_candidatos]

            for tamano in range(2, maximo_facturas + 1):

                for combo in combinations(candidatos, tamano):

                    suma = sum(valor for _, valor in combo)

                    if cls._coincide_valor(objetivo, suma):

                        return [
                            (tipo_doc, doc_id, valor, "combinado")
                            for doc_id, valor in combo
                        ]

        return None

    @classmethod
    def _buscar_pago_parcial(
        cls,
        db,
        extracto: ExtractoBancario,
    ) -> tuple[str, int, float, str] | None:
        objetivo = float(extracto.valor or 0)

        if objetivo <= 0:
            return None

        referencia = str(
            extracto.referencia or "",
        ).upper()

        descripcion = str(
            extracto.descripcion or "",
        ).upper()

        tipo_doc, facturas = cls._facturas_pendientes_por_tipo(
            db,
            extracto,
        )

        facturas = cls._filtrar_por_ventana_fecha(
            facturas,
            extracto,
        )

        for factura in facturas:

            saldo = float(
                factura.saldo_pendiente or factura.total or 0,
            )

            if not (0 < objetivo < saldo):
                continue

            if factura.numero and cls._coincide_texto(
                referencia,
                descripcion,
                factura.numero,
            ):

                return (
                    tipo_doc,
                    factura.id,
                    objetivo,
                    "parcial",
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
    def listar_pendientes(cls) -> list[ExtractoBancario]:
        db = SessionLocal()

        try:
            return (
                db.query(ExtractoBancario)
                .filter(
                    ExtractoBancario.conciliado.is_(False),
                )
                .order_by(
                    ExtractoBancario.fecha.desc(),
                )
                .all()
            )

        finally:
            db.close()

    @classmethod
    def candidatos_documento(
        cls,
        extracto_id: int,
        *,
        limite: int = 20,
    ) -> list[dict]:
        db = SessionLocal()

        try:
            extracto = db.get(
                ExtractoBancario,
                extracto_id,
            )

            if extracto is None:
                return []

            candidatos = (
                cls._candidatos_debito(db)
                if extracto.tipo == "debito"
                else cls._candidatos_credito(db)
            )

            candidatos.sort(
                key=lambda fila: abs(
                    fila["valor"] - float(extracto.valor or 0),
                ),
            )

            return candidatos[:limite]

        finally:
            db.close()

    @classmethod
    def _nombres_terceros(cls, db, ids: set[int]) -> dict[int, str]:
        from aplicacion.maestros.terceros.modelos import Tercero

        ids = {id_ for id_ in ids if id_}

        if not ids:
            return {}

        return {
            tercero.id: tercero.nombre_completo
            for tercero in (
                db.query(Tercero)
                .filter(Tercero.id.in_(ids))
                .all()
            )
        }

    @classmethod
    def _candidatos_debito(cls, db) -> list[dict]:
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )
        from aplicacion.modulos.tesoreria.comprobantes_egreso.modelos import (
            ComprobanteEgreso,
        )

        egresos = (
            db.query(ComprobanteEgreso)
            .filter(ComprobanteEgreso.activo.is_(True))
            .all()
        )

        facturas = (
            db.query(FacturaCompra)
            .filter(FacturaCompra.estado_pago == "pendiente")
            .all()
        )

        nombres = cls._nombres_terceros(
            db,
            {e.proveedor_id for e in egresos}
            | {f.proveedor_id for f in facturas},
        )

        candidatos = [
            {
                "tipo_documento": "comprobante_egreso",
                "documento_id": egreso.id,
                "numero": egreso.numero,
                "tercero": nombres.get(egreso.proveedor_id, ""),
                "valor": float(egreso.valor_total or 0),
                "fecha": egreso.fecha,
            }
            for egreso in egresos
        ]

        candidatos += [
            {
                "tipo_documento": "factura_compra",
                "documento_id": factura.id,
                "numero": factura.numero,
                "tercero": (
                    nombres.get(factura.proveedor_id, "")
                    or factura.razon_social_proveedor
                    or ""
                ),
                "valor": float(
                    factura.saldo_pendiente or factura.total or 0,
                ),
                "fecha": factura.fecha,
            }
            for factura in facturas
        ]

        return candidatos

    @classmethod
    def _candidatos_credito(cls, db) -> list[dict]:
        from aplicacion.modulos.tesoreria.recibos_caja.modelos import (
            ReciboCaja,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        recibos = (
            db.query(ReciboCaja)
            .filter(ReciboCaja.activo.is_(True))
            .all()
        )

        facturas = (
            db.query(FacturaVenta)
            .filter(FacturaVenta.estado_pago == "pendiente")
            .all()
        )

        nombres = cls._nombres_terceros(
            db,
            {r.cliente_id for r in recibos}
            | {f.cliente_id for f in facturas},
        )

        candidatos = [
            {
                "tipo_documento": "recibo_caja",
                "documento_id": recibo.id,
                "numero": recibo.numero,
                "tercero": nombres.get(recibo.cliente_id, ""),
                "valor": float(recibo.valor_total or 0),
                "fecha": recibo.fecha,
            }
            for recibo in recibos
        ]

        candidatos += [
            {
                "tipo_documento": "factura_venta",
                "documento_id": factura.id,
                "numero": factura.numero,
                "tercero": nombres.get(factura.cliente_id, ""),
                "valor": float(
                    factura.saldo_pendiente or factura.total or 0,
                ),
                "fecha": factura.fecha,
            }
            for factura in facturas
        ]

        return candidatos

    @classmethod
    def conciliar_manual(
        cls,
        extracto_id: int,
        tipo_documento: str,
        documento_id: int,
    ) -> ConciliacionBancaria:
        if tipo_documento not in (
            "comprobante_egreso",
            "factura_compra",
            "recibo_caja",
            "factura_venta",
        ):
            raise ValueError("Tipo de documento no soportado.")

        db = SessionLocal()

        try:
            extracto = db.get(
                ExtractoBancario,
                extracto_id,
            )

            if extracto is None:
                raise ValueError("Movimiento bancario no encontrado.")

            if extracto.conciliado:
                raise ValueError("El movimiento ya está conciliado.")

            registro = ConciliacionBancaria(
                extracto_id=extracto.id,
                tipo_documento=tipo_documento,
                documento_id=documento_id,
                valor=extracto.valor,
                estado="manual",
            )

            db.add(registro)
            extracto.conciliado = True

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    @classmethod
    def deshacer(cls, conciliacion_id: int) -> None:
        db = SessionLocal()

        try:
            registro = db.get(
                ConciliacionBancaria,
                conciliacion_id,
            )

            if registro is None:
                raise ValueError("Conciliación no encontrada.")

            extracto = db.get(
                ExtractoBancario,
                registro.extracto_id,
            )

            if extracto is not None:
                extracto.conciliado = False

            db.delete(registro)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    @classmethod
    def listar_conciliadas(cls) -> list[ConciliacionBancaria]:
        db = SessionLocal()

        try:
            return (
                db.query(ConciliacionBancaria)
                .order_by(
                    ConciliacionBancaria.fecha_creacion.desc(),
                )
                .limit(100)
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
