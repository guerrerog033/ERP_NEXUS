# Roadmap funcional ERP NEXUS v1.0

Documento alineado con el diagnóstico arquitectónico (agosto 2026) y el estado real del repositorio.

> **Nota:** `documentacion/PLAN_DESARROLLO.md` es histórico. Este documento y `docs/Arquitectura-v1.0.md` son la referencia vigente.

## Principio rector

No agregar pantallas sueltas hasta consolidar la cadena:

```
Maestros → Productos/Variantes → Documentos → Inventario → Cartera/Tesorería → DIAN → Impresión
```

## Estado real vs ZIP de revisión

Muchos ítems marcados como «faltantes» en una revisión externa **ya existen** en el código actual:

| Área | Estado en repo |
|------|----------------|
| Framework formularios/tablas/CRUD | ✅ Fases 1–7 |
| Productos + variantes + listas precio | ✅ Maestros + catálogo variantes |
| Impuestos | ✅ Maestro + seeds IVA |
| Inventario kardex/movimientos | ✅ `MovimientoInventario`, ajustes, traslados |
| Ventas cotización→factura | ✅ Flujo comercial A–G |
| Motor documental PDF/HTML | ✅ Fases 16–20 |
| Cartera / tesorería base | ✅ Recibos, egresos, CxC/CxP |

## Fase 21 — Consolidación maestros ✅ (esta entrega)

| Ítem | Estado |
|------|--------|
| Eliminar legacy `base_datos/modelos.py`, `terceros/entidad.py` | ✅ CI |
| Tercero multi-rol (`es_cliente`, `es_proveedor`, …) | ✅ |
| Perfiles `PerfilCliente`, `PerfilProveedor` | ✅ Modelo |
| Direcciones y contactos tercero | ✅ Modelo |
| Maestros: unidades, formas pago, medios pago, vendedores, atributos | ✅ Modelo + seeds |
| Impuestos: cuenta contable, código DIAN | ✅ |
| Bodegas: dirección, ciudad, responsable | ✅ |
| Empresa: tabla `empresa_bancos` | ✅ Modelo |
| Numeración documental (`numeracion_documentos`) | ✅ Modelo |
| Trazabilidad (`documento_vinculos`) | ✅ Modelo + hooks ventas |
| Alembic `0013_fase21_consolidacion` | ✅ |

## Orden de desarrollo recomendado (siguientes fases)

### Fase 22 — UI maestros base

CRUD (sin lógica nueva) para:

- Unidades de medida
- Formas y medios de pago
- Vendedores
- Atributos / valores
- Perfiles cliente y proveedor en formulario tercero
- Numeración documental

### Fase 23 — Productos definitivos

- FK `unidad_medida_id` en producto (reemplazar combo hardcoded)
- Variante → existencia por bodega (UI)
- Deprecar campo `existencia` en producto (solo kardex)

### Fase 24 — Numeración en runtime

- Servicio que consuma `NumeracionDocumento` + resolución DIAN
- Reemplazar contadores ad hoc en ventas/compras

### Fase 25 — Empresa emisora completa

- UI logo, bancos, sucursales
- Resoluciones por tipo documento (relacionar con numeración)

### Fase 26 — DIAN real

- Pipeline XML UBL → firma → envío → CUFE → eventos
- Recepción XML proveedor (separado de consulta terceros)

### Fase 27 — Auditoría y permisos por operación

- Eventos documentales (anulación, envío DIAN, impresión)
- Permisos granulares por documento/acción

## Modelo tercero (decisión adoptada)

Un solo maestro **TERCERO** con roles combinables:

```
Tercero
├── es_cliente
├── es_proveedor
├── es_empleado
└── es_vendedor
     ↓
PerfilCliente / PerfilProveedor (1:1 opcional)
```

`tipo_tercero` se conserva como clasificación de entrada al maestro (compatibilidad UI).

## Trazabilidad documental

Cadena ventas registrada en `documento_vinculos`:

```
COTIZACION → PEDIDO_VENTA → REMISION → FACTURA_VENTA
```

Hooks activos en `ServicioPedido`, `ServicioRemision`, `ServicioFacturaVenta`.

## Referencias

- `docs/Arquitectura-v1.0.md` — fases técnicas
- `docs/Flujo-comercial-v1.0.md` — cadena comercial
- `docs/Motor-Documental-v1.0.md` — impresión
- `docs/DIAN-go-live-v1.0.md` — facturación electrónica
