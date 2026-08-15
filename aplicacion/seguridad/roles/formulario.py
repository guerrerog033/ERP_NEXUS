from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)
from aplicacion.seguridad.roles.datasource import (
    RolDataSource,
)
from aplicacion.seguridad.roles.rol_definition import (
    RolDefinition,
)
from aplicacion.seguridad.roles.servicios import (
    ServicioRol,
)


class FormularioRol(FormularioBase):

    titulo = "Roles"

    definition = RolDefinition

    datasource = RolDataSource

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self._checks_modulos: dict[str, QCheckBox] = {}
        self._check_total: QCheckBox | None = None

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _crear_botones(self):

        if self._check_total is None:

            self._crear_selector_modulos()

        super()._crear_botones()

    def _crear_selector_modulos(self):

        grupo = QGroupBox(
            "Módulos permitidos",
        )

        layout = QVBoxLayout(
            grupo,
        )

        self._check_total = QCheckBox(
            "Acceso total a todos los módulos (*)",
        )

        self._check_total.toggled.connect(
            self._alternar_acceso_total,
        )

        layout.addWidget(
            self._check_total,
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True,
        )

        contenedor = QWidget()

        modulos_layout = QVBoxLayout(
            contenedor,
        )

        for etiqueta, modulo_id in ServicioRol.modulos_para_formulario():

            check = QCheckBox(
                etiqueta,
            )

            self._checks_modulos[
                modulo_id
            ] = check

            modulos_layout.addWidget(
                check,
            )

        modulos_layout.addStretch()

        scroll.setWidget(
            contenedor,
        )

        scroll.setMaximumHeight(
            220,
        )

        layout.addWidget(
            scroll,
        )

        self.card.agregar_widget(
            grupo,
        )

        if self.es_edicion:

            self._cargar_modulos()

    def _alternar_acceso_total(
        self,
        activo: bool,
    ):

        for check in self._checks_modulos.values():

            check.setEnabled(
                not activo,
            )

            if activo:

                check.setChecked(
                    False,
                )

    def _cargar_modulos(self):

        if self.datasource is None:

            return

        registro = self.datasource.obtener_por_id(
            self.id_registro,
        )

        if registro is None:

            return

        modulos = list(
            registro.modulos or [],
        )

        if "*" in modulos:

            if self._check_total is not None:

                self._check_total.setChecked(
                    True,
                )

            return

        for modulo_id, check in self._checks_modulos.items():

            check.setChecked(
                modulo_id in modulos,
            )

    def _modulos_seleccionados(self) -> list[str]:

        if (
            self._check_total is not None
            and self._check_total.isChecked()
        ):

            return ["*"]

        return [
            modulo_id
            for modulo_id, check in self._checks_modulos.items()
            if check.isChecked()
        ]

    def guardar(self):

        if self.datasource is None:

            raise RuntimeError(
                "No existe datasource configurado.",
            )

        try:

            datos = self.formulario.valores()

            datos["modulos"] = (
                self._modulos_seleccionados()
            )

            objeto = self.datasource.guardar(
                datos,
                self.id_registro,
            )

            self.guardar_exitoso(
                objeto,
            )

        except Exception as error:

            self.mostrar_error(
                str(error),
            )
