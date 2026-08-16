from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from aplicacion.maestros.terceros.datasource import (
    TerceroDataSource,
)

from aplicacion.framework.ui.lista_registros_widget import (
    CampoRegistro,
    ListaRegistrosWidget,
)

from aplicacion.maestros.terceros.portal_acceso_widget import (
    PortalAccesoWidget,
)

from aplicacion.maestros.terceros.servicio_registros import (
    ServicioContactoTercero,
    ServicioCuentaBancariaTercero,
    ServicioDireccionTercero,
)

from aplicacion.maestros.terceros.terceros_definition import (
    TerceroDefinition,
)


class TerceroFormulario(FormularioBase):

    titulo = "Terceros"

    ancho = 900

    alto = 780

    definition = TerceroDefinition

    datasource = TerceroDataSource

    CAMPOS_EXTERNOS = (

        "razon_social",
        "nombre_comercial",
        "primer_nombre",
        "segundo_nombre",
        "primer_apellido",
        "segundo_apellido",
        "direccion",
        "ciudad",
        "departamento",
        "pais",
        "telefono",
        "celular",
        "correo",

    )

    CAMPOS_AUTOCOMPLETAR = (

        "razon_social",
        "nombre_comercial",
        "primer_nombre",
        "segundo_nombre",
        "primer_apellido",
        "segundo_apellido",
        "direccion",
        "ciudad",
        "departamento",
        "telefono",
        "celular",
        "correo",

    )

    CAMPOS_PERSONA = (

        "primer_nombre",
        "segundo_nombre",
        "primer_apellido",
        "segundo_apellido",

    )

    CAMPOS_EMPRESA = (

        "razon_social",
        "nombre_comercial",

    )

    def __init__(
        self,
        id_registro=None,
        tipo_tercero_inicial=None,
        parent=None,
        *,
        modo=None,
    ):

        self._consultando = False

        self._tipo_tercero_inicial = tipo_tercero_inicial

        super().__init__(
            id_registro=id_registro,
            parent=parent,
            modo=modo,
        )

        self._aplicar_tipo_tercero_inicial()

        self._agregar_registros_relacionados()

    def _agregar_registros_relacionados(
        self,
    ) -> None:

        if not self.es_edicion:

            return

        opciones_tipo_cuenta = [
            ("Ahorros", "Ahorros"),
            ("Corriente", "Corriente"),
        ]

        secciones = (
            (
                "Direcciones",
                ServicioDireccionTercero,
                [
                    ("etiqueta", "Etiqueta"),
                    ("direccion", "Dirección"),
                    ("ciudad", "Ciudad"),
                    ("departamento", "Departamento"),
                    ("principal", "Principal"),
                ],
                [
                    CampoRegistro(
                        "etiqueta",
                        "Etiqueta",
                    ),
                    CampoRegistro(
                        "direccion",
                        "Dirección",
                        requerido=True,
                    ),
                    CampoRegistro(
                        "ciudad",
                        "Ciudad",
                    ),
                    CampoRegistro(
                        "departamento",
                        "Departamento",
                    ),
                    CampoRegistro(
                        "pais",
                        "País",
                    ),
                    CampoRegistro(
                        "principal",
                        "Dirección principal",
                        tipo="bool",
                    ),
                ],
                "Dirección",
            ),
            (
                "Contactos",
                ServicioContactoTercero,
                [
                    ("nombre", "Nombre"),
                    ("cargo", "Cargo"),
                    ("telefono", "Teléfono"),
                    ("correo", "Correo"),
                    ("principal", "Principal"),
                ],
                [
                    CampoRegistro(
                        "nombre",
                        "Nombre",
                        requerido=True,
                    ),
                    CampoRegistro(
                        "cargo",
                        "Cargo",
                    ),
                    CampoRegistro(
                        "telefono",
                        "Teléfono",
                    ),
                    CampoRegistro(
                        "correo",
                        "Correo",
                    ),
                    CampoRegistro(
                        "principal",
                        "Contacto principal",
                        tipo="bool",
                    ),
                ],
                "Contacto",
            ),
            (
                "Cuentas bancarias",
                ServicioCuentaBancariaTercero,
                [
                    ("banco", "Banco"),
                    ("tipo_cuenta", "Tipo"),
                    ("numero_cuenta", "Número"),
                    ("titular", "Titular"),
                    ("principal", "Principal"),
                ],
                [
                    CampoRegistro(
                        "banco",
                        "Banco",
                        requerido=True,
                    ),
                    CampoRegistro(
                        "tipo_cuenta",
                        "Tipo de cuenta",
                        tipo="combo",
                        opciones=opciones_tipo_cuenta,
                    ),
                    CampoRegistro(
                        "numero_cuenta",
                        "Número de cuenta",
                        requerido=True,
                    ),
                    CampoRegistro(
                        "titular",
                        "Titular",
                    ),
                    CampoRegistro(
                        "principal",
                        "Cuenta principal",
                        tipo="bool",
                    ),
                ],
                "Cuenta bancaria",
            ),
        )

        self._widgets_registros_relacionados = []

        grupo = QGroupBox(
            "Registros relacionados",
        )

        layout_botones = QHBoxLayout(
            grupo,
        )

        for (
            titulo_pestana,
            servicio,
            columnas,
            campos,
            titulo_dialogo,
        ) in secciones:

            widget = ListaRegistrosWidget(
                servicio=servicio,
                columnas=columnas,
                campos=campos,
                titulo_dialogo=titulo_dialogo,
                parent=self,
            )

            widget.hide()

            widget.cargar(
                self.id_registro,
            )

            self._widgets_registros_relacionados.append(
                widget,
            )

            layout_botones.addWidget(
                self._boton_registro_relacionado(
                    titulo_pestana,
                    widget,
                ),
            )

        widget_portal = PortalAccesoWidget(
            self.id_registro,
            parent=self,
        )

        widget_portal.hide()

        layout_botones.addWidget(
            self._boton_registro_relacionado(
                "Portal",
                widget_portal,
            ),
        )

        layout_botones.addStretch()

        self.card.agregar_widget(
            grupo,
        )

    def _boton_registro_relacionado(
        self,
        titulo: str,
        widget,
    ) -> QPushButton:

        boton = QPushButton(
            titulo,
        )

        boton.clicked.connect(
            lambda: self._abrir_ventana_registro(
                titulo,
                widget,
            ),
        )

        return boton

    def _abrir_ventana_registro(
        self,
        titulo: str,
        widget,
    ) -> None:

        ventana = QDialog(
            self,
        )

        ventana.setWindowTitle(
            titulo,
        )

        ventana.resize(
            720,
            480,
        )

        layout = QVBoxLayout(
            ventana,
        )

        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        layout.addWidget(
            widget,
        )

        ventana.exec()

        widget.setParent(
            self,
        )

        widget.hide()

    def _configurar_eventos(
        self,
    ) -> None:

        self.context.cambiar(
            "numero_documento",
            lambda _valor: self._documento_changed(),
        )

        self.context.cambiar(
            "tipo_documento",
            lambda _valor: self._tipo_documento_changed(),
        )

    def _preparar_campos_retencion(
        self,
    ):

        from aplicacion.maestros.impuestos.retenciones_catalogo import (
            opciones_retencion_combo,
        )
        from aplicacion.maestros.impuestos.servicios import (
            ServicioImpuesto,
        )

        ServicioImpuesto.inicializar_predeterminados()

        mapa_campos = {
            "retefuente_id": "Retefuente",
            "reteica_id": "ReteICA",
            "reteiva_id": "ReteIVA",
        }

        for grupo in self.definition.grupos:

            for campo in grupo.campos:

                tipo = mapa_campos.get(
                    campo.nombre,
                )

                if tipo is None:

                    continue

                campo.opciones = list(
                    opciones_retencion_combo(
                        tipo,
                    ),
                )

        if not self.es_edicion:

            for grupo in self.definition.grupos:

                for campo in grupo.campos:

                    if (
                        campo.nombre
                        != "reteiva_id"
                    ):

                        continue

                    campo.valor_inicial = None

    def _crear_formulario(self):

        if self.definition is None:

            return

        self._preparar_campos_retencion()

        super()._crear_formulario()

    def _aplicar_tipo_tercero_inicial(
        self,
    ) -> None:

        if (
            self.es_edicion
            or not self._tipo_tercero_inicial
        ):

            return

        tipo = self.widget(
            "tipo_tercero",
        )

        if tipo is None:

            return

        self.formulario.set_valor(
            "tipo_tercero",
            self._tipo_tercero_inicial,
        )

    def _tipo_documento_changed(
        self,
        _indice=None,
    ):

        if self._consultando:

            return

        dv = self.widget(
            "dv"
        )

        if dv is not None:

            dv.setText("")

        numero = self.widget(
            "numero_documento"
        )

        if (
            numero is not None
            and numero.text().strip()
        ):

            self._documento_changed()

    def _documento_changed(self):

        if self._consultando:

            return

        tipo = self.widget(
            "tipo_documento"
        )

        numero = self.widget(
            "numero_documento"
        )

        dv = self.widget(
            "dv"
        )

        if (
            tipo is None
            or numero is None
            or dv is None
        ):

            return

        numero_texto = numero.text().strip()

        if not numero_texto:

            dv.setText("")

            self._limpiar_campos_externos()

            return

        self._consultando = True

        try:

            try:

                resultado = self.datasource.documento_changed(

                    tipo.currentText(),

                    numero_texto,

                )

            except ValueError as error:

                self.mostrar_error(
                    str(error)
                )

                return

            numero.blockSignals(
                True
            )

            numero.setText(

                resultado.numero

            )

            numero.blockSignals(
                False
            )

            dv.setText(

                resultado.dv

            )

            if (
                resultado.existe
                and resultado.tercero is not None
            ):

                self.cargar(

                    resultado.tercero

                )

                self.mostrar_info(

                    "El tercero ya existe en el sistema."

                )

                return

            self._limpiar_campos_externos()

            if self._aplicar_datos_externos(
                resultado,
            ):

                mensaje = (
                    resultado.mensaje
                    or "Datos cargados desde consulta externa."
                )

                if resultado.estado_rut:

                    mensaje = (
                        f"{mensaje}\n"
                        f"Estado RUT: {resultado.estado_rut}"
                    )

                self.mostrar_info(
                    mensaje
                )

                return

            if resultado.error:

                self.mostrar_error(
                    resultado.error
                )

                return

            mensaje = (
                resultado.mensaje
                or (
                    "No se encontraron datos para este documento "
                    "en RUT/DIAN. Complete la información manualmente."
                )
            )

            self.mostrar_info(
                mensaje
            )

        finally:

            self._consultando = False

    def _limpiar_campos_externos(
        self,
    ) -> None:

        for campo in self.CAMPOS_EXTERNOS:

            self.formulario.set_valor(
                campo,
                "",
            )

    def _aplicar_datos_externos(
        self,
        resultado,
    ) -> bool:

        if not any(
            getattr(
                resultado,
                campo,
            )
            for campo in self.CAMPOS_AUTOCOMPLETAR
        ):

            return False

        tipo_widget = self.widget(
            "tipo_documento",
        )

        tipo = str(
            resultado.tipo
            or (
                tipo_widget.currentText()
                if tipo_widget is not None
                else ""
            )
        ).upper()

        es_juridica = self._es_persona_juridica(
            tipo,
            resultado,
        )

        for campo in self.CAMPOS_EXTERNOS:

            valor = getattr(
                resultado,
                campo,
            ) or ""

            self.formulario.set_valor(
                campo,
                valor,
            )

        if es_juridica:

            self._limpiar_campos(
                self.CAMPOS_PERSONA,
            )

        else:

            if (
                not resultado.primer_nombre
                and not resultado.primer_apellido
                and resultado.razon_social
            ):

                self._distribuir_nombre_persona(
                    resultado.razon_social,
                )

            self.formulario.set_valor(
                "razon_social",
                "",
            )

            self.formulario.set_valor(
                "nombre_comercial",
                "",
            )

        if not resultado.pais:

            self.formulario.set_valor(
                "pais",
                "Colombia",
            )

        return True

    def _es_persona_juridica(
        self,
        tipo: str,
        resultado,
    ) -> bool:

        if tipo == "NIT":

            return True

        if (
            resultado.primer_nombre
            or resultado.primer_apellido
        ):

            return False

        return bool(
            resultado.razon_social
        )

    def _limpiar_campos(
        self,
        campos,
    ) -> None:

        for campo in campos:

            self.formulario.set_valor(
                campo,
                "",
            )

    def _distribuir_nombre_persona(
        self,
        nombre_completo: str,
    ) -> None:

        partes = nombre_completo.split()

        if len(partes) >= 4:

            self.formulario.set_valor(
                "primer_nombre",
                partes[0],
            )

            self.formulario.set_valor(
                "segundo_nombre",
                partes[1],
            )

            self.formulario.set_valor(
                "primer_apellido",
                partes[2],
            )

            self.formulario.set_valor(
                "segundo_apellido",
                " ".join(
                    partes[3:]
                ),
            )

            return

        if len(partes) == 3:

            self.formulario.set_valor(
                "primer_nombre",
                partes[0],
            )

            self.formulario.set_valor(
                "primer_apellido",
                partes[1],
            )

            self.formulario.set_valor(
                "segundo_apellido",
                partes[2],
            )

            return

        if len(partes) == 2:

            self.formulario.set_valor(
                "primer_nombre",
                partes[0],
            )

            self.formulario.set_valor(
                "primer_apellido",
                partes[1],
            )

            return

        if len(partes) == 1:

            self.formulario.set_valor(
                "primer_nombre",
                partes[0],
            )
