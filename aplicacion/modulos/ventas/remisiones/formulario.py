from aplicacion.modulos.ventas.comunes.formulario_documento import (
    FormularioDocumentoVenta,
)
from aplicacion.modulos.ventas.remisiones.datasource import (
    RemisionDataSource,
)
from aplicacion.modulos.ventas.remisiones.servicios import (
    ServicioRemision,
)


class FormularioRemision(
    FormularioDocumentoVenta,
):

    titulo = "Remisión"

    servicio_generador = ServicioRemision

    datasource_cls = RemisionDataSource

    mensaje_guardado = "Remisión guardada correctamente."
