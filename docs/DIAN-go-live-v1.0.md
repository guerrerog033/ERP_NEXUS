# DIAN — Checklist go-live v1.0

Guía operativa para pasar de **habilitación** a **producción** con ERP NEXUS.

---

## Resumen del flujo

```text
Empresa + certificado
        ↓
Habilitación DIAN (SETP, test set)
        ↓
Pruebas ERP (mock + DIAN_E2E=1)
        ↓
Resolución y prefijos de producción
        ↓
Corte: ambiente_emision = produccion
        ↓
Monitoreo post go-live
```

---

## 1. Pre-requisitos

| Ítem | Config / acción |
|------|-----------------|
| NIT empresa | `empresa.nit` = NIT del certificado |
| Datos emisor | `empresa.nombre`, `direccion`, `ciudad`, `correo` |
| Certificado digital | `dian.certificado_ruta` (.p12/.pfx accesible) |
| Clave certificado | `dian.certificado_clave` (no commitear) |
| Resolución FE | `dian.resolucion_*` (número, vigencia, rango) |
| Carpeta XML | `dian.carpeta_xml_venta` con permisos de escritura |
| Emisión activa | `dian.emision_habilitada = true` |

Dependencias de firma (si aún no están instaladas):

```powershell
.venv\Scripts\pip.exe install lxml signxml cryptography
```

---

## 2. Habilitación DIAN

Archivo: `configuracion/configuracion.json` → sección `dian`.

| Clave | Valor típico habilitación |
|-------|---------------------------|
| `ambiente_emision` | `habilitacion` |
| `prefijo_factura` | `SETP` |
| `test_set_id` | ID del set de pruebas DIAN |
| `software_id` / `software_pin` | Según registro proveedor tecnológico |

### Validación automática

```powershell
cd C:\Proyectos\ERP_NEXUS
.venv\Scripts\python.exe scripts\dian\verificar_go_live.py --ambiente habilitacion
```

Debe mostrar **LISTO** (sin bloqueantes).

### Pruebas ERP

```powershell
# Mock (CI / sin red DIAN)
.venv\Scripts\python.exe -m pytest tests/integration/test_dian_e2e.py -q -k mock

# Emisión real en habilitación (requiere DB + certificado)
$env:DB_HOST="localhost"
$env:DIAN_E2E="1"
.venv\Scripts\python.exe -m pytest tests/integration/test_dian_e2e.py -m dian -q
```

Recorrido manual sugerido:

1. Factura → **Emitir DIAN** (o confirmar con emisión).
2. NC / ND desde factura contabilizada → emitir.
3. Descargar contenedor ZIP (`dian.contenedor_incluir_pdf`).
4. Verificar CUFE en catálogo (`dian.url_catalogo_cufe`).

---

## 3. Corte a producción

**No cambiar** hasta completar habilitación y tener resolución de numeración real.

| Clave | Habilitación | Producción |
|-------|--------------|------------|
| `ambiente_emision` | `habilitacion` | `produccion` |
| `prefijo_factura` | `SETP` | Prefijo autorizado (ej. `FV`) |
| `test_set_id` | Obligatorio | **Vacío** |
| `resolucion_*` | Set prueba | Resolución real vigente |
| Rango consecutivos | Prueba | Según resolución |

Alinear también `ventas.prefijo_factura` con la numeración operativa del ERP.

### Validación pre-corte

```powershell
.venv\Scripts\python.exe scripts\dian\verificar_go_live.py --ambiente produccion
```

Corrija todos los **bloqueantes** antes del cambio.

### Backup

1. Respaldo PostgreSQL (`copias_seguridad.ruta` o herramienta DBA).
2. Copia de `configuracion/configuracion.json`.
3. Ventana de corte acordada (evitar medio día operativo).

---

## 4. Post go-live

| Control | Frecuencia |
|---------|------------|
| Facturas rechazadas / `estado_dian` | Diario |
| Consecutivos vs resolución | Semanal |
| Vigencia certificado y resolución | Mensual |
| ZIP/XML en `carpeta_xml_venta` | Por emisión |
| Arqueo POS vs facturas emitidas | Diario (si aplica) |

Endpoints usados por el ERP:

- Habilitación: `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc`
- Producción: `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc`

---

## 5. API del validador

```python
from aplicacion.integraciones.dian.go_live import ValidadorGoLiveDian

resultado = ValidadorGoLiveDian.verificar_produccion()
# resultado["listo"], ["bloqueantes"], ["avisos"]

print(ValidadorGoLiveDian.resumen_texto(resultado))
```

Tests unitarios: `tests/unit/test_dian_go_live.py`.

---

## Referencias

- [Flujo-comercial-v1.0.md](./Flujo-comercial-v1.0.md) — bloques comerciales y DIAN E2E
- `configuracion/configuracion.json` — claves `dian.*`
- `tests/integration/test_dian_e2e.py` — emisión mock y real opcional
