# Flujo comercial y consolidación de maestros — v1.0

Documento de referencia tras los bloques **A–D** (estabilización de maestros, Terceros, Productos y demo comercial).

## Resumen de bloques completados

| Bloque | Objetivo | Entregable principal |
|--------|----------|----------------------|
| **A** | Patrón `*_table.py` en todos los maestros | `impuestos_table`, `listas_precio_table`, `empresas_table` + tests |
| **B** | Terceros listos para producción | Validación servicio, formulario, lookups Cliente/Proveedor |
| **C** | Productos alineados con kardex | Existencia solo lectura; variantes preservan stock en BD |
| **D** | Vertical slice comercial | Cliente → Producto → Cotización → Pedido/Factura + PDF DIAN |
| **E** | Cadena logística + post-venta | Remisión→Factura sin doble inventario; NC/ND desde factura confirmada |
| **F** | Post-venta transaccional | `confirmar_generacion` NC/ND; cartera y recibos de caja |
| **G** | UX operativa + E2E | Confirmar NC/ND en UI; tests vista; E2E comercial; POS verificado |

---

## Patrón maestros (`*_table.py`)

Todos los maestros base siguen:

```
maestros/<entidad>/
├── modelos.py
├── repositorio.py
├── servicios.py          (o servicio.py)
├── *_definition.py       → FormDefinition
├── *_table.py            → TableDefinition exportada
├── formulario.py
└── maestro.py            → CrudMaster
```

| Maestro | Tabla |
|---------|-------|
| Terceros | `terceros_table.py` → `TerceroTable` |
| Productos | `productos_table.py` → `ProductoTable` |
| Categorías | `categorias_table.py` → `CategoriaTable` |
| Marcas | `marcas_table.py` → `MarcaTable` |
| Impuestos | `impuestos_table.py` → `ImpuestoTable` |
| Listas de precio | `listas_precio_table.py` → `ListaPrecioTable` |
| Empresas | `empresas_table.py` → `EmpresaTable` |

En la definición del formulario:

```python
from aplicacion.maestros.<entidad>.<entidad>_table import EntidadTable

class EntidadDefinition(FormDefinition):
    table_definition = EntidadTable
```

---

## Terceros (Bloque B)

### Capacidades verificadas

- Validación NIT (DV automático, razón social obligatoria).
- Persona natural (CC + nombre/apellido).
- Responsabilidad fiscal por defecto (`resp_r99_pn` si no hay ninguna marcada).
- Eventos de formulario: cambio de tipo documento, consulta externa, autocompletado, retenciones.
- Lookups **Cliente** y **Proveedor** filtrados por `tipo_tercero` (usados en cotizaciones, compras, POS, cartera).

### Tests

| Archivo | Alcance |
|---------|---------|
| `tests/unit/test_tercero_validacion.py` | Servicio |
| `tests/unit/test_tercero_formulario.py` | FormEngine + eventos |
| `tests/unit/test_tercero_lookups.py` | ClienteLookup / ProveedorLookup |

---

## Productos (Bloque C)

### Regla de existencia

- **Formulario principal:** campo `existencia` deshabilitado (referencia; stock real = kardex).
- **Variantes:** columna `Existencia (ref.)` solo lectura en UI.
- **Al guardar variantes:** `_validar_variantes` **no** toma existencia del formulario; conserva el valor en BD por código de variante; variantes nuevas inician en `0`.

### Tests

| Archivo | Alcance |
|---------|---------|
| `tests/unit/test_producto_validacion.py` | Servicio + variantes + kardex |
| `tests/unit/test_producto_formulario.py` | FormEngine + widget variantes |

---

## Flujo comercial (Bloque D)

### Diagrama

```
                    ┌─────────────┐
                    │   Empresa   │ (config DIAN / prefijos)
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │ Cliente  │     │ Producto │     │ Impuesto │
   │ (Tercero)│     │ + IVA    │     │ IVA 19%  │
   └────┬─────┘     └────┬─────┘     └──────────┘
        │                │
        └────────┬───────┘
                 ▼
          ┌─────────────┐
          │ Cotización  │
          └──────┬──────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Pedido  │ │Remisión │ │ Factura │
└─────────┘ └─────────┘ └────┬────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              PDF / vista      Contenedor DIAN
              gráfica          (XML + PDF local)
```

### Servicios involucrados

| Paso | Servicio | Método clave |
|------|----------|--------------|
| Maestros | `TerceroServicio`, `ServicioProducto` | `guardar` / `guardar_completo` |
| Cotización | `ServicioCotizacion` | `guardar_completa(cabecera, lineas)` |
| Pedido | `ServicioPedido` | `crear_desde_cotizacion(id)` |
| Remisión | `ServicioRemision` | `crear_desde_cotizacion(id)`, `despachar(id)` |
| Factura | `ServicioFacturaVenta` | `crear_desde_cotizacion(id)`, `crear_desde_remision(id)` |
| Confirmar | `IntegracionFacturaVenta` | `confirmar_venta(id, emitir_dian=False)` → inventario + contabilidad |
| NC / ND | `IntegracionNotaCreditoVenta`, `IntegracionNotaDebitoVenta` | `crear_desde_factura(id)`, `confirmar_generacion(id)` |
| Tesorería | `IntegracionReciboCaja` | `contabilizar(id)` → abono parcial a facturas pendientes |
| PDF contenedor | `adjuntos_contenedor_factura_venta` | ZIP local XML + PDF |

La cotización puede generar **pedido**, **remisión** y **factura** de forma independiente (misma cotización, documentos distintos).

**Inventario:** si la remisión fue **despachada** (`inventario_aplicado`), al confirmar la factura vinculada no se descuenta stock de nuevo; solo se marca `inventario_aplicado` en la factura.

---

## Bloque E — Remisión → factura y notas

### E.1 Cadena remisión → factura

```
Cotización → Remisión → despachar() → Factura (desde remisión) → confirmar_venta()
                │                              │
                └── salida kardex (REM)        └── sin segunda salida si remisión despachada
```

### E.2 Notas crédito / débito

- `crear_desde_factura` acepta facturas en estado **`generada`**, **`emitida`** o **`contabilizada`**.
- NC copia líneas de la factura; ND crea línea de ajuste editable.
- Reversa de inventario en NC ocurre al **confirmar** (`confirmar_generacion`) o al emitir DIAN.

---

## Bloque F — Confirmación NC/ND y cartera

### F.1 `confirmar_generacion` (sin DIAN)

Paralelo a `confirmar_venta` en facturas:

| Documento | Efectos al confirmar |
|-----------|----------------------|
| **NC** | Reduce `saldo_pendiente` de la factura; entrada de inventario; contabilización automática |
| **ND** | Aumenta `saldo_pendiente` de la factura; contabilización automática |

API expuesta en controlador/datasource: `confirmar_generacion(id, emitir_dian=False)`.

### F.2 Recibos de caja

Tras factura contabilizada (`saldo_pendiente > 0`):

1. `ServicioReciboCaja.guardar_completo(cabecera, lineas)` — abono parcial o total.
2. `IntegracionReciboCaja.contabilizar(recibo_id)` — asiento + actualización de saldo y `estado_pago`.

`ServicioCartera.resumen()` refleja CxC pendiente tras abonos y NC.

---

## Tests automatizados

### Unitarios (sin PostgreSQL)

```powershell
cd C:\Proyectos\ERP_NEXUS
.venv\Scripts\python.exe -m pytest tests/unit/test_maestros_validacion.py tests/unit/test_maestros_formulario.py -q
.venv\Scripts\python.exe -m pytest tests/unit/test_tercero_validacion.py tests/unit/test_tercero_formulario.py tests/unit/test_tercero_lookups.py -q
.venv\Scripts\python.exe -m pytest tests/unit/test_producto_validacion.py tests/unit/test_producto_formulario.py -q
.venv\Scripts\python.exe -m pytest tests/unit/test_flujo_venta_basico.py tests/unit/test_notas_venta_basico.py -q
.venv\Scripts\python.exe -m pytest tests/unit/test_ventas_vista_e2e.py -q
.venv\Scripts\python.exe -m pytest tests/unit/test_fase10.py -q
```

### Integración (requiere PostgreSQL)

Configurar `.env` (ver `.env.example`): `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

```powershell
.venv\Scripts\python.exe -m pytest tests/integration/test_flujo_venta_basico.py -q -m integration
```

| Test | Qué valida |
|------|------------|
| `test_flujo_venta_cotizacion_a_factura` | Cliente + producto + cotización + factura en BD |
| `test_flujo_venta_cotizacion_a_pedido_y_pdf_contenedor` | + pedido + bytes PDF en contenedor DIAN |
| `test_flujo_venta_cotizacion_a_remision` | Cotización → remisión con `cotizacion_id` y `cliente_id` |
| `test_flujo_venta_confirmar_contabiliza_automatico` | Confirmar factura sin DIAN → `contabilizado` y `asiento_id` |
| `test_flujo_venta_remision_despacho_a_factura_sin_doble_inventario` | Despacho remisión + factura confirmada → una sola salida de kardex |
| `test_flujo_venta_nota_credito_desde_factura_confirmada` | NC borrador desde factura `contabilizada` |
| `test_flujo_venta_nota_debito_desde_factura_confirmada` | ND borrador desde factura `contabilizada` |
| `test_flujo_venta_nota_credito_confirmar_revierte_inventario_y_saldo` | NC confirmada → stock restaurado + saldo reducido |
| `test_flujo_venta_nota_debito_confirmar_aumenta_saldo` | ND confirmada → saldo factura aumenta |
| `test_flujo_tesoreria_recibo_caja_aplica_abono_parcial` | Recibo de caja contabilizado → abono 50 % |
| `test_flujo_e2e_comercial_completo` | E2E: factura → NC confirmada → recibo parcial |

Marcador `@pytest.mark.e2e` para el flujo comercial completo.

Los datos de prueba usan sufijos `uuid` para evitar colisiones entre ejecuciones.

---

## Checklist manual en UI

Recorrido recomendado para demo o aceptación:

1. **Empresas** — empresa activa con NIT, régimen y datos DIAN básicos.
2. **Terceros → Clientes** — NIT con DV o persona natural; guardar sin errores.
3. **Productos** — código, precio, IVA 19 %, stock mínimo; existencia deshabilitada.
4. **Ventas → Cotizaciones** — nuevo; lookup cliente; agregar línea de producto; guardar; **Confirmar** (borrador → aprobada).
5. Vista cotización → **Generar pedido** y/o **Facturar** (solo si está aprobada). **Cartera cliente** (resumen; ofrece detalle si hay saldo) y **Estado de cuenta** (modal con export PDF).
6. **Terceros → Clientes** — editar cliente → **Cartera cliente** / **Estado de cuenta**.
7. **Historial POS** — seleccionar venta → **Cartera cliente** / **Estado de cuenta**.
8. **Reportes → Comercial → Panel gerencial** — KPIs del periodo y embudo clicables.
9. **Facturas de venta** — abrir factura; **Confirmar**; vista previa / imprimir PDF.
10. (Opcional) Transmisión DIAN / descarga contenedor ZIP (XML + PDF según config `dian.contenedor_incluir_pdf`).

---

## Próximas fases sugeridas

| Prioridad | Tema | Notas |
|-----------|------|-------|
| 1 | **Recepción FE compras** | RADIAN y acuse automático |

### Completado en Bloque P

- **Dashboard gerencial:** `ServicioPanelGerencial.resumen(fecha_desde, fecha_hasta)` con KPIs de inicio, ventas/compras/utilidad del día, CxC/CxP, productos activos y pipeline del periodo.
- UI `PanelGerencialPage` con selector de fechas, KPIs clicables (navegan a módulos relacionados), embudo con barras de progreso y estilos QSS.
- **Estado de cuenta desde documentos comerciales:** `mostrar_estado_cuenta_cliente()` abre diálogo modal con `CarteraEstadoCuentaPage(bloquear_tercero=True)` y fallback directo si el lookup no resuelve el cliente.
- Helpers `cartera_desde_documento` / `estado_cuenta_desde_documento` en las 6 vistas comerciales; enlace cartera resumen → detalle cuando hay saldo.
- **Maestro Clientes:** botones Cartera / Estado de cuenta en edición (`ClienteFormulario`).
- **Historial POS:** botones Cartera / Estado de cuenta sobre la venta seleccionada (`cliente_id` en historial).
- Tests: `test_panel_gerencial.py`, `test_cartera_comercial.py` (modal bloqueado, fallback, enlace detalle), UI cotización en `test_ventas_vista_e2e.py`.

### Completado en Bloque O

- Validador `ValidadorGoLiveDian` (`aplicacion/integraciones/dian/go_live.py`).
- Script CLI: `scripts/dian/verificar_go_live.py` (`--ambiente habilitacion|produccion`).
- Documentación: [DIAN-go-live-v1.0.md](./DIAN-go-live-v1.0.md).
- Tests: `tests/unit/test_dian_go_live.py`.
- `.env.example`: variable `DIAN_E2E` documentada.

### Completado en Bloque N

- Botones **Ver factura** y **Cartera cliente** en `vista.py` de NC y ND.
- Navegación a `VistaFacturaVenta` vía `mostrar_dialogo_vista`.
- Tests UI: cartera y apertura de factura en `test_ventas_vista_e2e.py`.

### Completado en Bloque M

- `ServicioReportes.pipeline_comercial`: filas por cotización con pedido, remisión, factura, cobro y etapa actual.
- `pipeline_comercial_resumen`: conteos por etapa del embudo.
- UI `ReportePipelineComercialPage` (Reportes → Comercial → Pipeline cotización → cobro).
- Tests: `test_pipeline_comercial.py` (unit) + `test_reporte_pipeline_comercial_muestra_cadena_factura` (integración).

### Completado en Bloque L

- `ServicioPOSVenta.devolver_venta`: nota crédito desde venta POS (por `factura_id` o `log_id`).
- `RepositorioPosVentaLog.obtener_log_por_factura` para trazabilidad.
- Botón **Devolver venta** en `POSHistorialPage`.
- Tests integración: tarjeta vs efectivo esperado, devolución (saldo + inventario), cierre con diferencia de arqueo.
- Tests unitarios: `devolver_venta` y rechazo sin log POS.

### Completado en Bloque K

- Botón **Cartera cliente** en `vista_remision.py` (paridad con cotización, pedido y factura).
- Test UI: `test_vista_remision_cartera_invoca_resumen` en `test_ventas_vista_e2e.py`.

### Completado en Bloque J

- Cotizaciones nacen en **borrador**; `confirmar_cotizacion` → **aprobada**.
- Botón **Confirmar** y **Cartera cliente** en `vista_cotizacion.py`; wiring controlador/datasource.
- Operaciones bloqueadas si cotización en borrador: pedido, remisión y factura (`exigir_aprobada`).
- Cartera comercial: `ServicioCartera.resumen_cliente_cxc` + `mostrar_cartera_cliente` en vistas comerciales.
- Tests: `test_cartera_comercial.py`, `test_dian_e2e.py` (mock + opcional real con `DIAN_E2E=1`), UI cotización en `test_ventas_vista_e2e.py`.

### Completado en Bloque I

- Pedidos y remisiones nacen en **borrador**; `confirmar_pedido` / `confirmar_remision` → **pendiente**.
- Botón **Confirmar** en `vista_pedido.py` y `vista_remision.py`; wiring controlador/datasource.
- Operaciones bloqueadas en borrador: facturar, remisionar, reservar, despachar.
- Tests integración y UI ampliados.

### Completado en Bloque H

- Botón **Confirmar** en vista factura (`confirmar_venta` sin DIAN); wiring controlador/datasource.
- `pytest-qt` en dependencias; tests UI con `qtbot.mouseClick` en `test_ventas_vista_e2e.py`.
- Integración POS: `test_pos_facturar_registra_venta_inventario_y_log` (factura, inventario, log y caja).

### Completado en Bloque G

- Botón **Confirmar** en vistas NC y ND (`confirmar_generacion`).
- Factura: botones NC/ND habilitados en estado `contabilizada`.
- Tests UI: `tests/unit/test_ventas_vista_e2e.py`.
- Test E2E integración: `test_flujo_e2e_comercial_completo` (cotización → factura → NC parcial → recibo parcial).
- Fix recibos: al contabilizar, el abono descuenta del `saldo_pendiente` actual (respeta NC previas).
- POS Fase 10 verificado: cierre caja, reimpresión ticket, alertas stock (UI + `test_fase10.py` + `test_cerrar_caja_registra_arqueo`).

### Completado en Bloque F

- `IntegracionNotaCreditoVenta.confirmar_generacion` y ND equivalente.
- Efectos idempotentes: saldo + inventario NC; saldo ND.
- Recibo de caja: fix `es_anticipo` no persiste en modelo; test abono parcial.
- Recibo contabilizado: saldo se reduce desde `saldo_pendiente` (no recalcula solo `total - valor_pagado`).
- Wiring controlador/datasource para `confirmar_generacion`.

### Completado en Bloque E

- Test integración remisión despachada → factura sin doble inventario.
- NC y ND desde factura confirmada (`contabilizada`).
- Fix: `crear_desde_factura` acepta estado `contabilizada`.
- Unitarios `test_notas_venta_basico.py` y ampliación `test_flujo_venta_basico.py`.

### Completado en fase anterior

- Remisión en `test_flujo_venta_basico.py` (unit + integración).
- Contabilización automática al confirmar factura (`confirmar_venta` sin DIAN).
- Tablas `*_table.py` para cotizaciones, pedidos, remisiones, facturas, NC y ND.

---

## Referencias

- [DIAN-go-live-v1.0.md](./DIAN-go-live-v1.0.md) — checklist habilitación → producción.
- [Arquitectura-v1.0.md](./Arquitectura-v1.0.md) — fases del framework y stack.
- [Framework-v1.0.md](./Framework-v1.0.md) — patrones CRUD y carpetas oficiales.
