from __future__ import annotations


class FormContext:
    """
    Contexto compartido del formulario.
    """

    def __init__(self):

        self._formulario = None
        self._binding = None
        self._engine = None
        self._datasource = None
        self._widgets = {}
        self._contenedores = {}
        self._consultar_documento = None

    # ==================================================
    # Formulario
    # ==================================================

    @property
    def formulario(self):
        return self._formulario

    @formulario.setter
    def formulario(self, value):
        self._formulario = value

    # ==================================================
    # Engine
    # ==================================================

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    # ==================================================
    # Binding
    # ==================================================

    @property
    def binding(self):
        return self._binding

    @binding.setter
    def binding(self, value):
        self._binding = value

    # ==================================================
    # DataSource
    # ==================================================

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, value):
        self._datasource = value

    # ==================================================
    # Widgets
    # ==================================================

    def registrar_widget(
        self,
        nombre,
        widget,
    ):

        self._widgets[nombre] = widget

    def registrar_campo_contenedor(
        self,
        nombre: str,
        contenedor,
    ) -> None:

        self._contenedores[
            nombre
        ] = contenedor

    def marcar_error(
        self,
        nombre: str,
        mensaje: str,
    ) -> None:

        contenedor = self._contenedores.get(
            nombre,
        )

        if contenedor is None:

            return

        contenedor.marcar_error(
            mensaje,
        )

    def limpiar_error(
        self,
        nombre: str,
    ) -> None:

        contenedor = self._contenedores.get(
            nombre,
        )

        if contenedor is None:

            return

        contenedor.limpiar_error()

    def limpiar_errores(
        self,
    ) -> None:

        for contenedor in self._contenedores.values():

            contenedor.limpiar_error()

    def aplicar_errores(
        self,
        errores: dict,
    ) -> None:

        for nombre, mensaje in errores.items():

            self.marcar_error(
                nombre,
                str(
                    mensaje,
                ),
            )

    def widget(
        self,
        nombre,
    ):

        return self._widgets.get(
            nombre
        )

    # ==================================================
    # Valores
    # ==================================================

    def valor(
        self,
        nombre,
    ):

        if self._binding is None:
            return None

        return self._binding.valor(
            nombre
        )

    def set_valor(
        self,
        nombre,
        valor,
    ):

        if self._binding is None:
            return

        self._binding.set_valor(
            nombre,
            valor,
        )

    # ==================================================
    # Existe Widget
    # ==================================================

    def existe_widget(
        self,
        nombre,
    ):

        return nombre in self._widgets

    # ==================================================
    # API declarativa (formularios inteligentes)
    # ==================================================

    def campo(
        self,
        nombre: str,
    ):

        definicion = self._formulario

        if definicion is None:

            return None

        return definicion.buscar_campo(
            nombre,
        )

    def habilitar(
        self,
        nombre: str,
        valor: bool = True,
    ) -> None:

        widget = self.widget(
            nombre,
        )

        if widget is None:

            return

        if hasattr(
            widget,
            "setEnabled",
        ):

            widget.setEnabled(
                bool(
                    valor,
                ),
            )

    def mostrar(
        self,
        nombre: str,
        valor: bool = True,
    ) -> None:

        widget = self.widget(
            nombre,
        )

        if widget is None:

            return

        if hasattr(
            widget,
            "setVisible",
        ):

            widget.setVisible(
                bool(
                    valor,
                ),
            )

    def enfocar(
        self,
        nombre: str,
    ) -> None:

        widget = self.widget(
            nombre,
        )

        if widget is None:

            return

        if hasattr(
            widget,
            "setFocus",
        ):

            widget.setFocus()

    def cambiar(
        self,
        nombre: str,
        callback,
    ) -> None:

        if self._engine is None:

            return

        self._engine.on(
            f"campo:{nombre}",
            callback,
        )

    def configurar_consulta_documento(
        self,
        callback,
    ) -> None:
        self._consultar_documento = callback

    def consultar_documento(
        self,
        tipo_documento,
        numero_documento,
    ):
        if self._consultar_documento is not None:
            return self._consultar_documento(
                tipo_documento,
                numero_documento,
            )

        from aplicacion.dominio.documentos.consulta import consultar

        return consultar(
            tipo_documento,
            numero_documento,
        )