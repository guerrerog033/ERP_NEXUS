from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QFrame,
    QWidget,
    QDialog,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.form import FormEngine
from aplicacion.framework.form.validators import ValidationError
from aplicacion.framework.ui.card import Card
from aplicacion.recursos.ui.botones import Botones


class FormularioBase(Page):

    guardado = Signal()

    cerrar = Signal()

    titulo = "Formulario"

    definition = None

    datasource = None

    table_definition = None

    ancho = 900

    alto = 700

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        id_registro=None,
        parent=None,
        *,
        modo=None,
    ):

        super().__init__(
            parent
        )

        from aplicacion.framework.form.modo import (
            ModoFormulario,
            resolver_modo,
        )

        self.modo = resolver_modo(
            modo,
            id_registro,
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.setObjectName(
            "FormularioPage"
        )

        self.id_registro = id_registro

        self.es_edicion = (
            self.modo
            == ModoFormulario.EDICION
        )

        self.engine: FormEngine | None = None

        self._crear_datasource()

        self._crear_card()

        self._crear_formulario()

    def _en_dialogo(
        self,
    ) -> bool:

        return isinstance(
            self.parent(),
            QDialog,
        )

    # =====================================================
    # Datasource
    # =====================================================

    def _crear_datasource(self):

        if self.datasource is not None:

            self.datasource = self.datasource()

    # =====================================================
    # Card
    # =====================================================

    def _crear_card(self):

        titulo = ""

        if not self._en_dialogo():

            titulo = self.titulo

            if self.definition is not None:

                titulo = self.definition.titulo

        self.card = Card(
            titulo,
        )

        # Título alineado a la izquierda, igual que los documentos.
        self.card.lbl_titulo.setObjectName(
            "DocumentoTituloHoja",
        )

        self.card.lbl_titulo.setAlignment(
            Qt.AlignLeft
            | Qt.AlignVCenter,
        )

        self.card.layout_principal.setContentsMargins(
            28,
            22,
            28,
            20,
        )

        self.card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.card.setMinimumWidth(
            0,
        )

        if self._en_dialogo():

            self.layout_principal.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            self.card.layout_principal.setContentsMargins(
                12,
                8,
                12,
                8,
            )

            self.card.contenido.setSpacing(
                8,
            )

            self.card.setMinimumHeight(
                0,
            )

        else:

            self.card.setMinimumHeight(
                420,
            )

            self._poner_barra_titulo(
                titulo,
            )

        self.layout_principal.addWidget(
            self.card,
        )

    def _poner_barra_titulo(
        self,
        titulo: str,
    ) -> None:
        """
        Barra de título de escritorio con el color del módulo desde
        donde se abrió el formulario ("Nuevo cliente", "Editar
        producto"...), igual que en los documentos.
        """

        if not titulo:

            return

        from aplicacion.framework.app_context import AppContext
        from aplicacion.framework.form.modo import ModoFormulario
        from aplicacion.framework.ui.colores_modulo import color_modulo
        from aplicacion.framework.ui.documento_escritorio import (
            BarraTituloDocumento,
        )

        area = getattr(
            AppContext,
            "area_trabajo",
            None,
        )

        modulo_id = getattr(
            area.currentWidget() if area is not None else None,
            "_modulo_id",
            None,
        ) or ""

        prefijo = {
            ModoFormulario.NUEVO: "Nuevo",
            ModoFormulario.EDICION: "Editar",
            ModoFormulario.CONSULTA: "Consultar",
        }.get(
            getattr(
                self,
                "modo",
                None,
            ),
            "",
        )

        texto = (
            f"{prefijo} · {titulo}"
            if prefijo
            else titulo
        )

        self.barra_titulo = BarraTituloDocumento(
            texto,
            color_modulo(
                modulo_id,
            ),
        )

        self.barra_titulo.caja_numero.hide()

        self.card.lbl_titulo.hide()

        self.card.lbl_titulo.setText(
            "",
        )

        self.card.layout_principal.insertWidget(
            0,
            self.barra_titulo,
        )

        self.card.layout_principal.setContentsMargins(
            0,
            0,
            0,
            14,
        )

        self.card.contenido.setContentsMargins(
            24,
            10,
            24,
            0,
        )

    # =====================================================
    # Formulario
    # =====================================================

    def _crear_formulario(self):

        if self.definition is None:

            return

        self.engine = FormEngine(
            self.definition
        )

        contenedor = QWidget()

        contenedor.setLayout(
            self.engine.construir()
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True,
        )

        scroll.setFrameShape(
            QFrame.NoFrame,
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )

        scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f8fafc;
                margin: 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #64748b;
                border-radius: 4px;
                min-height: 28px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )

        scroll.setWidget(
            contenedor,
        )

        self.card.agregar_widget(
            scroll,
        )

        self.card.contenido.setStretch(
            self.card.contenido.count() - 1,
            1,
        )

        if self.es_edicion:

            self._cargar_registro()

        self._configurar_eventos()

        self.engine.aplicar_modo(
            self.modo,
        )

        self._crear_botones()

    def _configurar_eventos(
        self,
    ) -> None:
        """
        Las subclases registran callbacks con
        ``self.formulario.context.cambiar(...)``.
        """

    @property
    def context(self):

        if self.engine is None:

            raise RuntimeError(
                "El formulario no ha sido construido."
            )

        return self.engine.context

    @property
    def formulario(self):

        if self.engine is None:

            raise RuntimeError(
                "El formulario no ha sido construido."
            )

        return self.engine

    # ==================================================
    # Cargar
    # ==================================================

    def _cargar_registro(self):

        if self.datasource is None:

            return

        objeto = self.datasource.obtener_por_id(
            self.id_registro
        )

        if objeto is not None:

            self.formulario.cargar(
                objeto
            )

    # =====================================================
    # Botones
    # =====================================================

    def _registrar_atajos_formulario(
        self,
    ) -> None:

        from aplicacion.framework.ui.atajos import (
            pulsar,
            registrar_atajos,
        )

        # Enter pasa al siguiente campo, como Tab (FiltroTeclado).
        self.setProperty(
            "enter_avanza",
            True,
        )

        registrar_atajos(
            self,
            (
                (("Ctrl+S", "F10"), lambda: pulsar(self.btn_guardar)),
                ("Escape", self._cerrar_con_escape),
            ),
        )

        self.btn_guardar.setToolTip(
            "Guardar (Ctrl+S)",
        )

    def _cerrar_con_escape(
        self,
    ) -> None:
        """Esc cierra; si se puede guardar, pregunta antes."""

        from PySide6.QtWidgets import QMessageBox

        if self.btn_guardar.isVisible():

            respuesta = QMessageBox.question(
                self,
                "Cerrar",
                "¿Cerrar sin guardar los cambios?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if respuesta != QMessageBox.Yes:

                return

        self.cerrar_formulario()

    def teclas_contexto(
        self,
    ) -> list:

        from aplicacion.framework.ui.atajos import pulsar

        teclas = []

        if self.btn_guardar.isVisibleTo(
            self,
        ):

            teclas.append(
                ("F10", "Guardar", lambda: pulsar(self.btn_guardar)),
            )

        teclas += [
            ("Tab", "Siguiente campo", lambda: self.focusNextChild()),
            ("Esc", "Cerrar", self._cerrar_con_escape),
        ]

        return teclas

    def _crear_botones(self):

        from aplicacion.framework.form.modo import (
            ModoFormulario,
        )

        layout = QHBoxLayout()

        layout.addStretch()

        self.btn_guardar = Botones.guardar()

        self.btn_cancelar = Botones.cancelar()

        if self.modo == ModoFormulario.CONSULTA:
            self.btn_guardar.hide()
            self.btn_cancelar.setText(
                "Cerrar",
            )
        else:
            self.btn_guardar.clicked.connect(
                self.guardar
            )

        self.btn_cancelar.clicked.connect(
            self.cerrar_formulario
        )

        layout.addWidget(
            self.btn_guardar
        )

        layout.addWidget(
            self.btn_cancelar
        )

        self.card.agregar_layout(
            layout
        )

        self._registrar_atajos_formulario()

    @property
    def widgets(self):

        return self.formulario.widgets

    def widget(
        self,
        nombre,
    ):

        return self.formulario.widget(
            nombre
        )

    def cargar(
        self,
        objeto,
    ):

        self.formulario.cargar(
            objeto
        )

    def valores(self):

        return self.formulario.valores()

    def actualizar(
        self,
        objeto,
    ):

        return self.formulario.actualizar(
            objeto
        )

    # =====================================================
    # Mensajes
    # =====================================================

    def mostrar_error(
        self,
        mensaje,
    ):

        QMessageBox.critical(
            self,
            "Error",
            str(mensaje),
        )

    def mostrar_info(
        self,
        mensaje,
    ):

        QMessageBox.information(
            self,
            "Información",
            str(mensaje),
        )

    # =====================================================
    # Eventos
    # =====================================================

    def guardar_exitoso(
        self,
        objeto=None,
        mensaje="Registro guardado correctamente.",
    ):

        self.guardado.emit()

        self.mostrar_info(
            mensaje
        )

        self.cerrar.emit()

    def cerrar_formulario(self):

        self.cerrar.emit()

    # =====================================================
    # Guardar
    # =====================================================

    def guardar(self):

        if self.datasource is None:

            raise RuntimeError(
                "No existe datasource configurado."
            )

        try:

            objeto = self.datasource.guardar(

                self.valores(),

                self.id_registro,

            )

            self.guardar_exitoso(
                objeto
            )

        except ValidationError:

            return

        except Exception as e:

            self.mostrar_error(
                str(e)
            )