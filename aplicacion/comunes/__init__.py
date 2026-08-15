"""
Capa de persistencia y servicios compartidos del ERP.

Mantiene las bases de repositorio, servicio, controlador y utilidades
de exportación usadas por todos los módulos de negocio.

La UI vive en ``aplicacion.framework`` (Form, Table, CRUD, Documento).
"""

from aplicacion.comunes.controlador_base import ControladorBase
from aplicacion.comunes.exportacion import (
    boton_exportar_excel,
    exportar_tabla_excel,
)
from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.comunes.servicio_base import ServicioBase

__all__ = [
    "ControladorBase",
    "ServicioBase",
    "RepositorioBase",
    "exportar_tabla_excel",
    "boton_exportar_excel",
]
