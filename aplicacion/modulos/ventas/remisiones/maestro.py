from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.ventas.remisiones.datasource import (
    RemisionDataSource,
)
from aplicacion.modulos.ventas.remisiones.formulario import (
    FormularioRemision,
)
from aplicacion.modulos.ventas.remisiones.remision_definition import (
    RemisionDefinition,
)
from aplicacion.modulos.ventas.remisiones.vista_remision import (
    VistaRemision,
)


class FormularioRemisionLista:

    definition = RemisionDefinition


class MaestroRemisiones(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Remisiones internas"

    titulo_singular = "Remisión interna"

    datasource = RemisionDataSource

    formulario = FormularioRemisionLista

    vista_documento = VistaRemision

    def crear_formulario(
        self,
        id_registro=None,
        parent=None,
        *,
        modo=None,
    ):

        kwargs = {
            "id_registro": id_registro,
        }

        if parent is not None:

            kwargs["parent"] = parent

        return FormularioRemision(
            **kwargs,
        )

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        remision = self.datasource.obtener_completa(
            id_registro,
        )

        if remision is None:

            return "Remisión interna"

        return f"Remisión interna {remision.numero}"

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
    ) -> str:

        if id_registro is not None:

            return "Editar remisión interna"

        return "Nueva remisión interna"

    def _tamanio_dialogo_formulario(
        self,
        formulario,
    ) -> tuple[int, int]:

        margen = self._margen_dialogo_formulario()

        ancho = min(
            formulario.ancho,
            max(
                1100,
                self.width() - margen,
            ),
        )

        alto = min(
            formulario.alto,
            max(
                520,
                self.height() - margen,
            ),
        )

        return ancho, alto
