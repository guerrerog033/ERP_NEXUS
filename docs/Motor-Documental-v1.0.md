# Motor documental ERP NEXUS v1.0

Documento de referencia para representación gráfica (PDF, vista previa, impresión y correo).

## Estado real vs revisión externa

La revisión del ZIP describía `aplicacion/reportes/` como vacío. **En el repo actual ya existe un motor operativo** con más de 50 archivos:

| Capa | Ruta | Rol |
|------|------|-----|
| Adaptadores por módulo | `aplicacion/reportes/` | HTML + PDF ReportLab por tipo de documento |
| Framework de impresión | `aplicacion/framework/reportes/` | Motor dual HTML/Qt + ReportLab, centro de impresión |
| **Capa canónica (nueva)** | `aplicacion/documentos/impresion/` | DTOs, catálogo, componentes compartidos, renderers |

No se duplicó la lógica de negocio: se **consolidó** la arquitectura propuesta al inicio del proyecto.

## Arquitectura objetivo

```
Documento comercial (ORM)
        │
        ▼
datos_documento.py  →  dict / DocumentoDatos
        │
        ▼
ReporteDocumentoBase  (aplicacion.reportes.*)
        │
        ├─ generar_html()     → Vista previa / impresión Qt
        └─ construir_pdf_reportlab() → ReportLab
                │
                ▼
        componentes compartidos (encabezado, tercero, detalle, totales, QR, pie)
```

Para factura electrónica:

```
Factura comercial
    ├─ Representación gráfica (PDF/HTML)  ← este documento
    └─ XML UBL + DIAN + CUFE + QR         ← integraciones/dian (fase posterior)
```

## Catálogo oficial (26 formatos)

Definido en `aplicacion/documentos/impresion/catalogo.py`:

| Código | Documento |
|--------|-----------|
| 01 | Cotización |
| 02 | Pedido venta |
| 03 | Remisión |
| 04 | Factura venta |
| 05 | Nota crédito |
| 06 | Nota débito |
| 07 | Recibo caja |
| 08–26 | Compras, inventario, contabilidad, tesorería |

Cada entrada indica si soporta ReportLab, HTML o ambos.

## Componentes reutilizables

Ubicación: `aplicacion/documentos/impresion/componentes/`

| Componente | Uso |
|------------|-----|
| `encabezado` | Logo + empresa + título + número |
| `tercero` | Bloque cliente/proveedor |
| `detalle` | Tabla comercial, logística, aplicación cartera |
| `pie` | QR, CUFE, estado DIAN, observaciones |
| `firmas` | Recibido por / firma (remisiones) |

Los PDF existentes en `aplicacion/reportes/ventas/pdf/` se están migrando a estos componentes (factura y remisión ya parcialmente integrados).

## Formatos de página

Configurados en `aplicacion/framework/reportes/formatos_pagina.py`:

- Carta (8.5 × 11)
- Media carta
- A4
- Tirilla 58 mm / 80 mm

El mismo documento puede renderizarse en distinto tamaño vía `formato_pagina` del renderer.

## API recomendada para módulos

```python
from aplicacion.documentos.impresion import (
    abrir_centro_documento,
    exportar_documento_pdf,
)
from aplicacion.reportes.ventas.factura import ReporteFacturaVenta

reporte = ReporteFacturaVenta(factura, detalles, nombre_cliente)
abrir_centro_documento(reporte, parent=self)
```

Render directo ReportLab vía catálogo:

```python
from aplicacion.documentos.impresion.formatos import crear_renderer
from aplicacion.reportes.comunes.datos_documento import factura_venta_a_dto

renderer = crear_renderer(
    "04_FACTURA_VENTA",
    factura_venta_a_dto(factura, detalles, nombre, electronica=True),
    archivo=ruta_pdf,
    electronica=True,
)
renderer.construir_pdf()
```

## Diseño visual acordado (factura electrónica)

Checklist de campos soportados en DTO + PDF factura:

- [x] Empresa (razón social, NIT, dirección, contacto)
- [x] Número y título documento
- [x] Fecha generación / vencimiento
- [x] Forma y medio de pago
- [x] Cliente (documento, dirección, contacto)
- [x] Detalle (cantidad, precio, descuento, impuestos, total)
- [x] Subtotal, descuento, impuestos, total
- [x] Valor en letras
- [x] CUFE, QR, autorización/resolución, estado DIAN
- [x] Observaciones
- [ ] Logo empresa (soportado si `empresa.logo` apunta a archivo válido)

## Próximos pasos del motor

1. ~~Migrar cotización, pedido, recibo y egreso a componentes compartidos.~~ ✅ Fase 18
2. ~~PDF dedicados para nota crédito/débito (hoy reutilizan layout de factura).~~ ✅ Fase 19
3. ~~Remisión: tabla logística con cantidad entregada vs solicitada desde DTO.~~ ✅ Fase 19
4. ~~Recibo caja: bloque “aplicado a facturas” con saldos.~~ ✅ Fase 18
5. ~~Unificar HTML (`formatos_impresion.py`) para usar los mismos DTOs.~~ ✅ Fase 20

## Tests

- `tests/unit/test_motor_pdf_reportlab.py` — cobertura amplia de reportes existentes
- `tests/unit/test_motor_documentos.py` — catálogo, DTOs, renderer factura/cotización/pedido/recibo/egreso

## Regla de evolución

- **No** crear PDFs aislados por módulo sin pasar por `DocumentoDatos` + componentes.
- **No** mezclar XML DIAN con layout PDF.
- **Sí** usar `abrir_centro_documento` para vista previa, PDF, impresión y correo con un solo renderer.
