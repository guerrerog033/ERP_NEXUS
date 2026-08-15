# ERP NEXUS

> ERP moderno, modular y mantenible desarrollado en Python con PySide6 y SQLAlchemy.

---

# Descripción

ERP NEXUS es un sistema ERP desarrollado con una arquitectura modular propia.

El proyecto está dividido en dos grandes partes:

- Framework NEXUS
- Módulos del ERP

El Framework proporciona la infraestructura común necesaria para construir nuevos módulos de forma rápida, consistente y reutilizable.

Los módulos contienen exclusivamente la lógica de negocio.

---

# Objetivos

- Arquitectura limpia.
- Código reutilizable.
- Bajo acoplamiento.
- Alta cohesión.
- Fácil mantenimiento.
- Fácil incorporación de nuevos módulos.
- Documentación técnica.
- Evolución controlada.

---

# Tecnologías

- Python 3
- PySide6
- SQLAlchemy
- SQLite (desarrollo)
- PostgreSQL (producción)

---

# Estructura del proyecto

```
ERP_NEXUS/

aplicacion/
    framework/
    maestros/
    compras/
    ventas/
    inventario/
    seguridad/

docs/

tests/

scripts/

recursos/

README.md
requirements.txt
```

---

# Framework NEXUS

El Framework contiene únicamente componentes reutilizables.

Actualmente está organizado en:

```
framework/

base/
crud/
formulario/
controls/
lookup/
ui/
database/
```

---

# Arquitectura

La arquitectura sigue una separación clara de responsabilidades.

```
Usuario

↓

UI

↓

Controlador

↓

Servicio

↓

Repositorio

↓

SQLAlchemy

↓

Base de datos
```

Cada capa conoce únicamente la capa inmediatamente inferior.

---

# Filosofía

ERP NEXUS sigue cinco principios fundamentales.

## Simplicidad

La solución más simple que resuelva correctamente el problema será la preferida.

## Consistencia

Todos los módulos siguen exactamente la misma estructura.

## Reutilización

El código común pertenece al Framework.

El código específico pertenece al módulo.

## Responsabilidad única

Cada clase tiene una única responsabilidad.

## Evolución controlada

Toda mejora importante debe estar justificada técnicamente.

---

# Metodología de desarrollo

Cada componente sigue el siguiente ciclo.

```
Análisis

↓

Diseño

↓

Implementación

↓

Pruebas

↓

Documentación

↓

Estable
```

---

# Estado del proyecto

Versión actual:

```
0.1.0
```

Estado:

```
En desarrollo
```

---

# Roadmap

## Foundation

- Framework Base
- CRUD
- FormEngine
- Toolbar
- Table

## Validación

- Marcas
- Categorías
- Empresas

## Core ERP

- Clientes
- Proveedores
- Productos
- Inventario

## Operación

- Compras
- Ventas

## Enterprise

- Dashboard
- Reportes
- Seguridad
- Auditoría

---

# Convenciones

Cada módulo del ERP tendrá la siguiente estructura.

```
modulo/

modelo.py

repositorio.py

servicio.py

controlador.py

formulario.py

maestro.py
```

---

# Licencia

Proyecto ERP NEXUS.

Todos los derechos reservados.
