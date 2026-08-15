# Framework NEXUS v1.0

Mapa oficial de carpetas bajo `aplicacion/framework/` y capas relacionadas.

## Principio de capas

| Capa | Ruta | Responsabilidad |
|------|------|-----------------|
| Dominio | `aplicacion/dominio/` | Reglas puras (DV, impuestos, totales) sin Qt ni BD |
| Framework | `aplicacion/framework/` | UI reutilizable, formularios, tablas, CRUD |
| Comunes | `aplicacion/comunes/` | Repositorios, servicios y controladores base (sin UI) |
| Interfaz | `aplicacion/interfaz/` | Shell Qt (sidebar, dashboard, login) |
| Recursos | `aplicacion/recursos/estilos/` | Design system (`tema.qss`, tokens) |
| Módulos | `aplicacion/modulos/` | Pantallas de negocio por área |
| Maestros | `aplicacion/maestros/` | CRUD de entidades maestras |

## `aplicacion/framework/` — mapa oficial

```
framework/
├── base/           Page, FormularioBase, MaestroBase
├── form/           FormEngine, FormBuilder, FormContext, FormEvents, fields
├── table/          TableEngine, definición de columnas
├── crud/           CrudMaster + mixins (único punto CRUD maestro)
├── datagrid/       Tabla con búsqueda en listados
├── documento/      DocumentoService, DocumentoResult (re-export DV → dominio)
├── datasource/     Adaptador SQLAlchemy → controladores UI
├── app_context.py  Contexto global de sesión/navegación
└── modulos.py      Re-export de menu_manifest.MODULOS
```

### Eliminado en Fase 12 y Fase 17 (no reintroducir)

- `framework/controles/` — widgets duplicados; usar `form/fields` + `recursos/ui`
- `framework/kernel/` — registry/events sin uso
- `framework/formulario_crud.py`, `maestro_crud.py` — sustituidos por `crud/`
- `framework/navegacion.py` — usar `interfaz/navegacion_usuario.py`
- `interfaz/estilos.py` — usar `recursos/estilos/tema.py`
- `base_datos/modelos.py` — modelos solo en `maestros/` y `modulos/`
- `comunes/maestro_base.py`, `comunes/formulario_base.py` — usar `framework/base/`
- `init_db.py` — usar `crear_bd.py` + `base_datos/inicializar.py`

## Dominio — documentos

```
dominio/
├── documentos/
│   ├── dv.py           DVCalculator / CalculadoraDV (NIT Colombia)
│   ├── resultado.py    DocumentoResult
│   ├── servicio.py     ServicioDocumento (preparar, fusionar, mensajes)
│   └── consulta.py     registro + consultar (puerto de infraestructura)
├── impuestos/
│   ├── linea.py        calcular_linea
│   └── totales.py      calcular_totales_lineas
└── credito/
    └── cupo.py         evaluar_cupo
```

Imports recomendados:

- **Nuevo código:** `from aplicacion.dominio.documentos.dv import DVCalculator`
- **Consulta documento:** `from aplicacion.dominio.documentos.consulta import consultar`
- **Compatibilidad UI:** `from aplicacion.framework.documento.dv import DVCalculator`
- **Widget documento:** `context.consultar_documento(tipo, numero)` (sin importar framework)

## Design system

```
recursos/estilos/
├── tema.qss        Estilos globales Qt (FormGroupBox, shell)
├── tema.py         aplicar_tema(app)
├── colores.py      Tokens PRIMARY, TEXT, Colores (alias legado)
├── dimensiones.py  ESPACIADO_*, RADIO_*, CONTROL_*
└── estilos.py      Estilos programáticos para botones/controles puntuales
```

## UX shell (Fase 13)

- `interfaz/barra_lateral.py` — sidebar colapsable (`ANCHO` 240 ↔ `ANCHO_COLAPSADO` 68)
- `interfaz/barra_superior.py` — búsqueda, alertas (`agregar_notificacion`), menú usuario
- `interfaz/inicio.py` — dashboard KPI (cotizaciones, cartera, maestros)
- `recursos/ui/botones.py` — `BotonPrimario`, `BotonSecundario`, `BotonPeligro` vía QSS
- `framework/form/campo_contenedor.py` — error visual debajo del control

## Patrones CRUD oficiales

### Maestro declarativo

```
*_definition.py   → FormDefinition (campos + layout)
*_table.py        → TableDefinition (columnas + filtros)   [opcional, recomendado]
formulario.py     → FormularioBase + definition
maestro.py        → CrudMaster + formulario + datasource
```

Ejemplo: `maestros/terceros/terceros_table.py` exporta `TerceroTable`; `TerceroDefinition.table_definition = TerceroTable`.

Maestros con tabla separada (Bloque A): Terceros, Productos, Categorías, Marcas, Impuestos, Listas de precio, Empresas. Detalle y tests en [Flujo-comercial-v1.0.md](../Flujo-comercial-v1.0.md).

### Documento comercial (Page + grid de líneas)

El listado CRUD **no** usa el mismo widget que el formulario de edición.

```
*_definition.py        → FormDefinition con table_definition (solo columnas)
maestro.py:
    class FormularioXLista:
        definition = XDefinition

    class MaestroX(CrudDocumento, CrudMaster):
        formulario = FormularioXLista

        def crear_formulario(...):
            return FormularioX(...)   # Page real
```

Referencia: `modulos/contabilidad/comprobantes/maestro.py`, `modulos/ventas/facturas/maestro.py`.

### Widgets

| Archivo | Responsabilidad |
|---------|-----------------|
| `form/widget_registry.py` | `registrar`, `obtener`, `existe`, `eliminar`, `limpiar`, `widgets` |
| `form/widget_factory.py` | Registro inicial de factories + `WidgetFactory.crear()` |

No duplicar mapas de factories fuera de `widget_factory.py`.

### Base de datos

| Archivo | Uso |
|---------|-----|
| `base_datos/registro_modelos.py` | **Única** lista de imports ORM |
| `base_datos/startup.py` | Login + migraciones Alembic |
| `base_datos/inicializar.py` | Script dev: `crear_tablas()` |
| `crear_bd.py` | Dev: tablas + usuario admin |

Producción: Alembic (`alembic upgrade head`), no `create_all()` manual.

### Capas (no mezclar)

| Capa | Ruta | No debe contener |
|------|------|------------------|
| Framework | `framework/` | SQL directo, reglas DIAN |
| Comunes | `comunes/` | Widgets Qt |
| Nucleo | `nucleo/` | Formularios |
| Dominio | `dominio/` | Qt, SQLAlchemy sessions |
| Maestros / Módulos | `maestros/`, `modulos/` | Lógica de widgets genéricos |

## DataGrid y CRUD (Fase 15)

- `datagrid/toolbar.py` — `MaestroToolbar`: Nuevo, Editar, Consultar, Eliminar, Más (Actualizar/Excel/PDF/Imprimir), búsqueda
- `datagrid/datagrid.py` — toolbar integrada + `LoadingOverlay`
- `crud/trabajo_listado.py` — consulta asíncrona en `CrudDatos`
- `form/modo.py` — `ModoFormulario` (nuevo / edición / consulta)
- `FormularioBase` + `FormEngine.aplicar_modo()` — consulta en solo lectura

## CI

```bash
python scripts/ci/inventario_codigo_muerto.py
python -m pytest tests/unit/test_fase12.py tests/unit/test_fase14.py tests/unit/test_fase15.py -q
python -m pytest tests/unit/test_flujo_venta_basico.py -q
python -m pytest tests/integration/test_flujo_venta_basico.py -q -m integration
```

Flujo comercial documentado en [Flujo-comercial-v1.0.md](../Flujo-comercial-v1.0.md).
