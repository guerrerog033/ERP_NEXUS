from aplicacion.documentos.impresion.componentes.detalle import (
    construir_aplicacion_cartera,
    construir_bloque_totales,
    construir_tabla_detalle,
    construir_tabla_logistica,
)
from aplicacion.documentos.impresion.componentes.encabezado import (
    construir_encabezado_empresa,
    construir_meta_documento,
)
from aplicacion.documentos.impresion.componentes.firmas import (
    construir_bloque_firmas,
)
from aplicacion.documentos.impresion.componentes.pie import (
    construir_observaciones,
    construir_pie_electronico,
)
from aplicacion.documentos.impresion.componentes.qr import (
    qr_imagen,
)
from aplicacion.documentos.impresion.componentes.tercero import (
    construir_bloque_tercero,
)

__all__ = [
    "construir_aplicacion_cartera",
    "construir_bloque_firmas",
    "construir_bloque_tercero",
    "construir_bloque_totales",
    "construir_encabezado_empresa",
    "construir_meta_documento",
    "construir_observaciones",
    "construir_pie_electronico",
    "construir_tabla_detalle",
    "construir_tabla_logistica",
    "qr_imagen",
]
