# NEXUS Core — Arquitectura oficial v1.0

Documento de referencia para consolidación del ERP.

## Estado de fases

### Fases 1–4 — Completadas

Ver secciones anteriores del documento. Resumen:

- Framework CRUD unificado, paginación, filtros declarativos, `QTableView`.
- Tipos `Numeric` en ventas, compras y tesorería.
- Auditoría por campo base en `ServicioBase.actualizar()`.

### Fase 5 — Completada

| Ítem | Estado |
|------|--------|
| `Numeric` en contabilidad, inventario, nómina y CRM | ✅ |
| Alembic `0004_numeric_fase5` | ✅ |
| `ColumnStyledDelegate` + `TextAlignmentRole` en `RegistrosModel` | ✅ |
| Auditoría en `guardar_completa` de documentos transaccionales | ✅ |
| `LookupFilterWidget` con diálogo de búsqueda | ✅ |

### Fase 6 — Completada

| Ítem | Estado |
|------|--------|
| `Numeric` logística (`COORDENADA`, `DINERO`) y POS (`pos_ventas_log`) | ✅ |
| Alembic `0005_numeric_fase6` | ✅ |
| `StatusColumn` + badges en `ColumnStyledDelegate` | ✅ |
| Auditoría cabecera + líneas en `guardar_completa()` | ✅ |
| Exportación CSV desde CRUD paginado (botón Excel) | ✅ |

### Fase 7 — Completada

| Ítem | Estado |
|------|--------|
| POS: captura recibido/cambio/método de pago en UI | ✅ |
| `StatusColumn` en pedidos, remisiones, notas, compras, tesorería | ✅ |
| Exportación Excel (openpyxl) desde CRUD paginado | ✅ |
| `auditoria_campos_linea` configurable por servicio | ✅ |

### Fase 8 — Completada

| Ítem | Estado |
|------|--------|
| Historial POS consultable (`POSHistorialPage`) | ✅ |
| Badges CRM, nómina y contabilidad | ✅ |
| Exportación PDF desde CRUD paginado | ✅ |
| Auditoría cabecera configurable (`auditoria_campos_cabecera*`) | ✅ |

### Fase 9 — Completada

| Ítem | Estado |
|------|--------|
| Filtros avanzados historial POS (pago, usuario) | ✅ |
| Ticket térmico POS (80 mm, QPrintDialog) | ✅ |
| Dashboard caja POS del día (`POSCajaPage`) | ✅ |
| CI GitHub Actions + verificación Alembic unificada | ✅ |

## Stack oficial

```
INTERFAZ → CRUD → FormEngine / TableEngine → DataSource → Repository → PostgreSQL
```

## Tipos monetarios

Usar `aplicacion.base_datos.tipos`:

- `DINERO` → `Numeric(18, 2)`
- `CANTIDAD` → `Numeric(18, 4)`
- `PORCENTAJE` → `Numeric(8, 4)`
- `TASA` → `Numeric(18, 6)`
- `COORDENADA` → `Numeric(10, 7)`

Migraciones Alembic: cadena unificada `0001_baseline` → `7c5b26130061` → `0002` … → `0006_fase10_pos`. CI ejecuta `scripts/ci/verificar_alembic.py` y `alembic upgrade head`.

## Auditoría documentos

Servicios transaccionales definen `entidad_auditoria` / `modulo_auditoria` y en `guardar_completa()`:

```python
cambios = cls.auditar_documento(id_registro, cabecera, lineas)
resultado = cls.repositorio.actualizar_completa(...)
cls.confirmar_auditoria_cabecera(id_registro, cambios)
```

Documentos integrados: cotizaciones, facturas venta, pedidos, remisiones, notas crédito/débito, facturas compra, documentos soporte.

## Filtros lookup con diálogo

```python
from aplicacion.framework.datagrid.filtros import LookupFilter
from aplicacion.maestros.terceros.cliente_lookup import ClienteLookup

LookupFilter(
    "cliente_id",
    etiqueta="Cliente",
    lookup=ClienteLookup,
)
```

El panel renderiza `LookupFilterWidget` con botón de búsqueda y `LookupDialog`.

## Tablas CRUD

`CrudMaster.usar_table_view = True` usa `QTableView` + `RegistrosModel` + `ColumnStyledDelegate` (incluye badges `StatusColumn`).

Exportación: botón **Excel** del grid exporta todos los registros (filtros activos) en `.xlsx` vía openpyxl; fallback CSV si no hay openpyxl. Botón **PDF** genera listado paginado en PDF (`exportar_registros_pdf`).

Auditoría cabecera: `auditoria_campos_cabecera` (lista blanca) o `auditoria_campos_cabecera_excluir` (lista negra) en `ServicioBase`.

## Fase 8 ✅

1. Historial POS consultable (`POSHistorial` en menú Ventas).
2. Badges en CRM, nómina y contabilidad.
3. Exportación PDF desde CRUD paginado.
4. Auditoría de cabecera con campos excluidos/configurables.

## Fase 9 ✅

1. Historial POS con filtros de método de pago y usuario.
2. Impresión de ticket térmico 80 mm al facturar (opcional).
3. Dashboard **Caja POS** con totales y desglose por método de pago.
4. Workflow CI (pytest + Alembic head) en `.github/workflows/ci.yml`.

## Fase 10 ✅

1. Cierre de caja POS con arqueo (`pos_cierres_caja`, sección en **Caja POS**).
2. Reimpresión de ticket desde historial POS.
3. Notificaciones de stock mínimo en POS (`stock_minimo` en productos + alertas en venta).
4. Tests de integración PostgreSQL en `tests/integration/` (CI con `-m integration`).

## Próximas fases (consolidación + UX)

Alineado con la revisión arquitectónica del proyecto (298 archivos `.py`). **No rehacer desde cero**; consolidar capas y elevar UX.

### Fase 11 — FormEngine y contexto ✅

| Ítem | Estado |
|------|--------|
| `FormContext`: `campo`, `habilitar`, `mostrar`, `enfocar`, `cambiar` | ✅ |
| Conectar señales Qt → `engine.emit("campo:…")` (`campo_signals.py`) | ✅ |
| Completar `FormEvents` (`emitir_cambio`, guardar/cancelar) | ✅ |
| QSS de grupos en `tema.qss` (`FormGroupBox`); tokens `colores.py` / `dimensiones.py` | ✅ |
| Hook `_configurar_eventos()` en `FormularioBase`; Terceros vía `context.cambiar` | ✅ |
| `DVCalculator` consolidado en `framework/documento/dv.py` | ✅ |

### Fase 12 — Limpieza arquitectónica ✅

| Ítem | Estado |
|------|--------|
| Inventario de código muerto (`interfaz/estilos.py`, `framework/controles`, `kernel`, CRUD legacy) | ✅ |
| Unificar estilos en `recursos/estilos/` (`colores.py`, `dimensiones.py` en `estilos.py`) | ✅ |
| Consolidar DV en `dominio/documentos/dv.py` (re-export framework + terceros) | ✅ |
| Mapa oficial de carpetas (`docs/Framework-v1.0.md`, `scripts/ci/inventario_codigo_muerto.py`) | ✅ |

### Fase 13 — UX shell ✅

| Ítem | Estado |
|------|--------|
| Sidebar colapsable + iconos PNG/SVG (`recursos/iconos`) | ✅ |
| Barra superior (búsqueda, notificaciones, menú usuario) — base en `BarraSuperior` | ✅ |
| Dashboard de negocio (KPIs, actividad reciente) | ✅ |
| Jerarquía visual de botones (primario / secundario / peligro) | ✅ |
| Validación visual en campos (error debajo del control) | ✅ |

### Fase 14 — Dominio ✅

| Ítem | Estado |
|------|--------|
| Capa `aplicacion/dominio/` (DV, documentos, impuestos, crédito) | ✅ |
| Terceros: `DocumentoService` / widget desacoplados vía `dominio.documentos.consulta` | ✅ |
| Tests de dominio antes que UI (`tests/unit/test_fase14.py`) | ✅ |

### Fase 15 — DataGrid y operación ✅

| Ítem | Estado |
|------|--------|
| Toolbar unificada (Nuevo, Editar, Eliminar, Más) | ✅ |
| Estados de carga (`LoadingOverlay` / workers) | ✅ |
| Modos Nuevo / Edición / Consulta en CRUD | ✅ |

### Seguridad y distribución

- `.env` en `.gitignore` ✅ — usar `.env.example` como plantilla.
- No distribuir `.venv`, `.git`, `.pytest_cache` ni `.env` en ZIPs del proyecto.
- Alembic idempotente en tablas opcionales ✅ (revisiones `0002`–`0004`).

## Fase 0.5 — Estabilización arquitectónica ✅

Consolidación previa a ampliar maestros y documentos comerciales.

| Ítem | Estado |
|------|--------|
| Eliminar `base_datos/modelos.py` (Empresa legacy en tabla `empresas`) | ✅ |
| Punto único de registro ORM: `registro_modelos.importar_modelos()` | ✅ |
| `inicializar.py` / `crear_bd.py` delegan a `registro_modelos` | ✅ |
| `main.py` sin imports parciales duplicados de modelos | ✅ |
| `WidgetRegistry` solo registro; factories en `widget_factory.py` | ✅ |
| `FormDefinition` + `TableDefinition` separables (`*_table.py`) | ✅ Todos los maestros base (ver [Flujo-comercial-v1.0.md](./Flujo-comercial-v1.0.md)) |
| Documentos venta: stub listado + `crear_formulario()` → Page | ✅ Facturas, pedidos, remisiones |
| Mensaje claro si falta `table_definition` en CRUD | ✅ |

### Orden recomendado antes de Fase 1 comercial

1. ~~Terminar Terceros~~ ✅ Bloque B
2. ~~Productos → Categorías → Marcas → Impuestos~~ ✅ Bloque A + C
3. ~~Cotización → Pedido → Factura~~ ✅ Bloque D (ver [Flujo-comercial-v1.0.md](./Flujo-comercial-v1.0.md))

Pendiente ampliar: ~~Remisión en test integración~~ ✅, ~~contabilización automática~~ ✅, ~~`*_table.py` en documentos de venta~~ ✅, ~~Bloque E remisión→factura y NC/ND~~ ✅.

### Regla de modelos

Cada maestro posee su modelo en `maestros/<entidad>/modelos.py`. No agregar modelos de negocio en `base_datos/`.

### Existencia de inventario

No almacenar `existencia` como campo editable en Producto; debe derivarse del kardex (entradas − salidas).

### Valoración vs código actual

| Área | Revisión externa | Estado real en repo |
|------|-----------------|---------------------|
| Framework formularios | 8/10 | ✅ `WidgetFactory`, `ocupa_fila_completa` (sin `if check` en Builder) |
| Alembic / migraciones | Prioridad alta | ✅ Cadena hasta `0006`, CI + integración |
| UX shell | 5–6/10 | ✅ Sidebar colapsable, barra superior con alertas, KPIs ampliados (Fase 13) |
| Terceros | Básico | ✅ Validación, formulario, lookups (Bloque B) |
| Tests framework / maestros | Insuficiente | ✅ `test_maestros_*`, `test_tercero_*`, `test_producto_*`, `test_flujo_venta_basico` |
| Estilos duplicados | 3 fuentes | ✅ `tema.qss` + tokens; legacy `interfaz/estilos.py` eliminado (Fase 12) |

### Fase 16 — Motor documental ✅

| Ítem | Estado |
|------|--------|
| Capa canónica `aplicacion/documentos/impresion/` (DTOs, catálogo 26 formatos, renderer) | ✅ |
| Componentes compartidos (encabezado, tercero, detalle, pie, firmas) | ✅ |
| Integración factura PDF + remisión (firmas/logística) | ✅ Parcial |
| Documentación `docs/Motor-Documental-v1.0.md` | ✅ |
| Tests `test_motor_documentos.py` | ✅ |

### Fase 17 — Saneamiento arquitectónico ✅

Consolidación posterior al motor documental: retirar restos legacy y blindar capas.

| Ítem | Estado |
|------|--------|
| Sin `base_datos/modelos.py` (Empresa duplicada) | ✅ |
| Sin stubs UI en `comunes/` (`maestro_base`, `formulario_base`) | ✅ |
| UI base solo en `framework/base/` | ✅ |
| Punto único ORM: `registro_modelos.importar_modelos()` | ✅ |
| Dev DB: `crear_bd.py` → `base_datos/inicializar.py` (sin `init_db.py`) | ✅ |
| Inventario CI ampliado (rutas + imports prohibidos) | ✅ `scripts/ci/inventario_codigo_muerto.py` |
| `.gitignore` reforzado (`.pytest_cache`, artefactos, ZIPs locales) | ✅ |
| Tests `test_fase17_saneamiento.py` | ✅ |

**No reintroducir:** `init_db.py`, `framework/navegacion.py`, `interfaz/estilos.py`, `framework/controles`, imports a `aplicacion.base_datos.modelos`.

Documento de mapa de capas: `docs/Framework-v1.0.md`. Plan histórico desactualizado: `documentacion/PLAN_DESARROLLO.md` (referencia únicamente).

### Fase 18 — Motor documental (formatos comerciales) ✅

| Ítem | Estado |
|------|--------|
| Cotización PDF → componentes compartidos | ✅ |
| Pedido PDF → componentes compartidos | ✅ |
| Recibo caja PDF + bloque cartera con saldos | ✅ |
| Comprobante egreso PDF + bloque cartera con saldos | ✅ |
| DTOs `_lineas_recibo_caja` / `_lineas_comprobante_egreso` con saldos | ✅ |
| HTML tesorería alineado (4 columnas cartera) | ✅ |
| Tests `crear_renderer` + `construir_aplicacion_cartera` | ✅ |

### Fase 19 — NC/ND y remisión logística ✅

| Ítem | Estado |
|------|--------|
| `NotaVentaPDF` dedicado (NC/ND con meta factura/motivo) | ✅ |
| Renderers catálogo `05_NOTA_CREDITO`, `06_NOTA_DEBITO` | ✅ |
| `remision_a_dto` con pedido, dirección y cantidades logísticas | ✅ |
| `RemisionPDF` con componentes compartidos + tabla logística | ✅ |
| HTML remisión: solicitada vs entregada | ✅ |

### Fase 20 — HTML unificado con DTOs ✅

| Ítem | Estado |
|------|--------|
| Puente `reportes/comunes/html_documento.py` | ✅ |
| Cotización / pedido / factura / remisión → `contexto_formato_desde_dto` | ✅ |
| Tesorería recibo y egreso → `html_comercial_desde_dto` | ✅ |
| Tests `test_html_documento.py` | ✅ |

**Pendiente:** formatos HTML avanzados de cotización (carta/corporativo) siguen usando `ContextoFormato` + detalles ORM para imágenes/IVA por línea; los datos base ya vienen del DTO.

### Fase 21 — Consolidación maestros y trazabilidad ✅

| Ítem | Estado |
|------|--------|
| Tercero multi-rol + perfiles cliente/proveedor | ✅ |
| Maestros: unidades, formas/medios pago, vendedores, atributos | ✅ Modelo |
| Numeración documental + vínculos entre documentos | ✅ |
| Empresa bancos, bodega enriquecida, impuesto DIAN/contable | ✅ |
| Hooks trazabilidad COT→PED→REM→FV | ✅ |
| Roadmap funcional `docs/Roadmap-funcional-v1.0.md` | ✅ |
| Alembic `0013_fase21_consolidacion` | ✅ |

**Siguiente:** Fase 22 — CRUD UI de maestros base (sin nueva lógica de negocio).

### Fase 22 — Producto e inventario (modelos) ✅

| Ítem | Estado |
|------|--------|
| `Producto` / `ProductoVariante` con `DINERO`/`CANTIDAD`, JSONB, relaciones ORM | ✅ |
| `precio_modelo.py` — `ProductoPrecio` por lista de precio (conserva `lista_precio_id`) | ✅ |
| Inventario: relaciones `Bodega` ↔ `ExistenciaBodega` ↔ `MovimientoInventario` | ✅ |
| `ExistenciaBodega.disponible`; existencia en producto = referencia kardex | ✅ |
| `ProductoVariante.nombre_completo` | ✅ |
| Alembic `0014_producto_inventario` | ✅ |
