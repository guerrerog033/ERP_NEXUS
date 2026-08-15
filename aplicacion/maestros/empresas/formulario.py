from __future__ import annotations

import re

from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)
from aplicacion.framework.documento import (
    DVCalculator,
)
from aplicacion.framework.form.validators import (
    ValidationError,
)
from aplicacion.integraciones.dian import DianServicio
from aplicacion.maestros.empresas.datasource import (
    EmpresaDataSource,
)
from aplicacion.maestros.empresas.empresa_definition import (
    EmpresaDefinition,
)
from aplicacion.maestros.empresas.logo_widget import (
    LogoEmpresaWidget,
)
from aplicacion.maestros.empresas.servicios import (
    EmpresaServicio,
)


class EmpresaFormulario(FormularioBase):

    titulo = "Empresas"

    definition = EmpresaDefinition

    datasource = EmpresaDataSource

    CAMPOS_AUTOCOMPLETAR = (

        "razon_social",
        "nombre_comercial",
        "direccion",
        "ciudad",
        "departamento",
        "telefono",
        "correo",

    )

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self._consultando = False

        super().__init__(
            id_registro=id_registro,
            parent=parent,
        )

        self._conectar_eventos()

        self._insertar_logo_widget()

    def _insertar_logo_widget(self):

        self.logo_widget = LogoEmpresaWidget()

        grupo = QGroupBox(
            "Logo",
        )

        layout = QVBoxLayout(
            grupo,
        )

        layout.addWidget(
            self.logo_widget,
        )

        self.card.contenido.insertWidget(
            self.card.contenido.count() - 1,
            grupo,
        )

        if self.es_edicion:

            registro = EmpresaServicio.obtener_por_id(
                self.id_registro,
            )

            if (
                registro is not None
                and registro.logo_ruta
            ):

                self.logo_widget.establecer_ruta_relativa(
                    registro.logo_ruta,
                )

    def guardar(self):

        if self.datasource is None:

            raise RuntimeError(
                "No existe datasource configurado."
            )

        try:

            datos = self.formulario.valores()

            archivo = self.logo_widget.archivo_pendiente()

            if archivo:

                datos["_logo_archivo"] = archivo

            elif self.logo_widget.ruta_relativa():

                datos["logo_ruta"] = (
                    self.logo_widget.ruta_relativa()
                )

            objeto = self.datasource.guardar(
                datos,
                self.id_registro,
            )

            self.guardar_exitoso(
                objeto,
            )

        except ValidationError:

            return

        except Exception as error:

            self.mostrar_error(
                str(error),
            )

    def _conectar_eventos(self):

        nit = self.widget(
            "nit"
        )

        if nit is None:

            return

        nit.editingFinished.connect(
            self._nit_changed
        )

        nit.returnPressed.connect(
            self._nit_changed
        )

    def _nit_changed(self):

        if self._consultando:

            return

        nit_widget = self.widget(
            "nit"
        )

        dv_widget = self.widget(
            "dv"
        )

        if (
            nit_widget is None
            or dv_widget is None
        ):

            return

        numero = re.sub(
            r"\D",
            "",
            nit_widget.text().strip(),
        )

        if not numero:

            dv_widget.setText("")

            self._limpiar_campos_externos()

            return

        dv_widget.setText(
            DVCalculator.calcular(
                numero
            )
        )

        nit_widget.blockSignals(
            True
        )

        nit_widget.setText(
            numero
        )

        nit_widget.blockSignals(
            False
        )

        self._consultando = True

        try:

            consulta = DianServicio.consultar(
                "NIT",
                numero,
            )

            if self._aplicar_datos_externos(
                consulta,
            ):

                mensaje = (
                    consulta.mensaje
                    or "Datos cargados desde consulta externa."
                )

                if consulta.estado_rut:

                    mensaje = (
                        f"{mensaje}\n"
                        f"Estado RUT: {consulta.estado_rut}"
                    )

                self.mostrar_info(
                    mensaje
                )

                return

            if consulta.error:

                self.mostrar_error(
                    consulta.error
                )

                return

            if consulta.mensaje:

                self.mostrar_info(
                    consulta.mensaje
                )

                return

            self.mostrar_info(
                "No se encontraron datos para este NIT en "
                "RUT/DIAN ni en RUES. Complete la información "
                "manualmente."
            )

        finally:

            self._consultando = False

    def _limpiar_campos_externos(
        self,
    ) -> None:

        for campo in self.CAMPOS_AUTOCOMPLETAR:

            self.formulario.set_valor(
                campo,
                "",
            )

    def _aplicar_datos_externos(
        self,
        consulta,
    ) -> bool:

        if not any(
            getattr(
                consulta,
                campo,
            )
            for campo in self.CAMPOS_AUTOCOMPLETAR
        ):

            return False

        for campo in self.CAMPOS_AUTOCOMPLETAR:

            valor = getattr(
                consulta,
                campo,
            ) or ""

            self.formulario.set_valor(
                campo,
                valor,
            )

        if consulta.dv:

            self.formulario.set_valor(
                "dv",
                consulta.dv,
            )

        if not consulta.pais:

            self.formulario.set_valor(
                "pais",
                "Colombia",
            )

        return True
