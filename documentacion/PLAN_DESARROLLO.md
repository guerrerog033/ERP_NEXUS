# ERP NEXUS

> **Nota (2026):** plan histórico actualizado. Use **`docs/Roadmap-funcional-v1.0.md`**, **`docs/Arquitectura-v1.0.md`** y **`docs/Framework-v1.0.md`**.

## Estado del Proyecto

Versión actual: **0.1.0** · Fases técnicas **1–21** completadas en código.

---

# Módulos

## Base del Sistema

- [x] Base de datos
- [x] SQLAlchemy + Alembic
- [x] Login
- [x] Empresa (maestro base; FE en configuración JSON)
- [x] Dashboard / KPIs inicio
- [x] Configuración

---

## Maestros

- [x] Terceros (multi-rol Fase 21)
- [x] Perfiles cliente / proveedor (modelo Fase 21)
- [x] Productos + variantes + listas precio
- [x] Categorías
- [x] Marcas
- [x] Bodegas (básico + campos logísticos Fase 21)
- [x] Impuestos
- [x] Unidades de medida (modelo Fase 21)
- [x] Formas / medios de pago (modelo Fase 21)
- [x] Vendedores (modelo Fase 21)
- [x] Atributos producto (modelo Fase 21)
- [ ] Centros de costo
- [ ] UI CRUD maestros Fase 21 (Fase 22)

---

## Inventario

- [x] Kardex / movimientos
- [x] Ajustes
- [x] Traslados
- [ ] Entradas / salidas (pantallas dedicadas)
- [ ] Existencia solo por kardex (deprecar campo producto)

---

## Compras

- [x] Órdenes, recepciones, facturas compra (base)
- [ ] Flujo completo producción + NC proveedor

---

## Ventas

- [x] Cotizaciones → pedidos → remisiones → facturas
- [x] NC / ND
- [x] POS
- [x] Trazabilidad documento_vinculos (Fase 21)

---

## Tesorería

- [x] Recibos de caja
- [x] Comprobantes de egreso
- [x] Conciliación bancaria (base)

---

## Cartera

- [x] Cuentas por cobrar / pagar (base)

---

## Contabilidad

- [x] Plan de cuentas, comprobantes (base)
- [ ] Reportes contables completos

---

## Reportes / impresión

- [x] Motor documental PDF/HTML (Fases 16–20)
- [x] Exportación CSV/Excel/PDF desde CRUD

---

## Administración

- [x] Usuarios / roles (base)
- [x] Auditoría por campo (base)
- [ ] Permisos por operación documental

---

## DIAN

- [x] Arquitectura consulta terceros (placeholder DIAN/RUES)
- [x] Config go-live (`docs/DIAN-go-live-v1.0.md`)
- [ ] Emisión / recepción XML real

---

# Objetivo

ERP Python + PySide6 + SQLAlchemy, arquitectura por capas, PostgreSQL, cadena maestros → documentos → inventario → cartera → DIAN.
