from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from aplicacion.integraciones.dian.cliente_recepcion import (
    ClienteRecepcionDian,
)
from aplicacion.integraciones.dian.servicio_recepcion import (
    ServicioRecepcionCompras,
)
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.ui.botones import Botones


class DialogoSincronizacionDian(QDialog):

    titulo = "Sincronizar facturas DIAN"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setWindowTitle(
            self.titulo,
        )

        self.setMinimumWidth(
            560,
        )

        self._crear_ui()
        self._cargar_configuracion()

    def _config(
        self,
    ) -> dict:

        return dict(
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {},
        )

    def _crear_ui(
        self,
    ) -> None:

        layout = QVBoxLayout(
            self,
        )

        descripcion = QLabel(
            "Conecte su token de integración DIAN "
            "(como en Cifra, Factus u otro proveedor). "
            "En modo automático el ERP importa las facturas "
            "recibidas y usted solo debe revisarlas y aprobar."
        )

        descripcion.setWordWrap(
            True,
        )

        layout.addWidget(
            descripcion,
        )

        formulario = QFormLayout()

        formulario.setSpacing(
            10,
        )

        self.chk_habilitado = QCheckBox(
            "Habilitar sincronización de compras",
        )

        self.txt_url = QLineEdit()

        self.txt_url.setPlaceholderText(
            "https://api.proveedor.com.co",
        )

        self.txt_token = QLineEdit()

        self.txt_token.setEchoMode(
            QLineEdit.EchoMode.Password,
        )

        self.txt_token.setPlaceholderText(
            "Token Bearer de su proveedor DIAN",
        )

        self.txt_nit = QLineEdit()

        self.txt_nit.setPlaceholderText(
            "NIT de su empresa (receptor)",
        )

        self.spn_dias = QSpinBox()

        self.spn_dias.setRange(
            1,
            365,
        )

        self.spn_dias.setValue(
            30,
        )

        self.chk_auto_cufe = QCheckBox(
            "Validar CUFE automáticamente al importar",
        )

        self.chk_auto_cufe.setChecked(
            True,
        )

        self.chk_modo_automatico = QCheckBox(
            "Modo automático (importar sin intervención)",
        )

        self.chk_sincronizar_inicio = QCheckBox(
            "Sincronizar al iniciar el ERP",
        )

        self.chk_sincronizar_compras = QCheckBox(
            "Sincronizar al abrir facturas de compra",
        )

        self.chk_crear_proveedor = QCheckBox(
            "Crear proveedor automáticamente si no existe",
        )

        self.chk_auto_acuse = QCheckBox(
            "Generar acuse de recibo en facturas a crédito",
        )

        self.chk_notificar = QCheckBox(
            "Notificar cuando lleguen facturas nuevas",
        )

        self.spn_intervalo = QSpinBox()

        self.spn_intervalo.setRange(
            5,
            1440,
        )

        self.spn_intervalo.setValue(
            30,
        )

        self.spn_intervalo.setSuffix(
            " min",
        )

        self.txt_listar = QLineEdit()

        self.txt_descargar = QLineEdit()

        self.txt_enviar_acuse = QLineEdit()

        formulario.addRow(
            "",
            self.chk_habilitado,
        )

        formulario.addRow(
            "URL base API",
            self.txt_url,
        )

        formulario.addRow(
            "Token",
            self.txt_token,
        )

        formulario.addRow(
            "NIT receptor",
            self.txt_nit,
        )

        formulario.addRow(
            "Días a consultar",
            self.spn_dias,
        )

        formulario.addRow(
            "",
            self.chk_auto_cufe,
        )

        formulario.addRow(
            "",
            self.chk_modo_automatico,
        )

        formulario.addRow(
            "Intervalo automático",
            self.spn_intervalo,
        )

        formulario.addRow(
            "",
            self.chk_sincronizar_inicio,
        )

        formulario.addRow(
            "",
            self.chk_sincronizar_compras,
        )

        formulario.addRow(
            "",
            self.chk_crear_proveedor,
        )

        formulario.addRow(
            "",
            self.chk_auto_acuse,
        )

        formulario.addRow(
            "",
            self.chk_notificar,
        )

        formulario.addRow(
            "Endpoint listar",
            self.txt_listar,
        )

        formulario.addRow(
            "Endpoint XML",
            self.txt_descargar,
        )

        formulario.addRow(
            "Endpoint acuse recibo",
            self.txt_enviar_acuse,
        )

        layout.addLayout(
            formulario,
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True,
        )

        self.log.setMaximumHeight(
            120,
        )

        layout.addWidget(
            self.log,
        )

        barra = QHBoxLayout()

        self.btn_probar = QPushButton(
            "Probar conexión",
        )

        self.btn_guardar = Botones.guardar()

        self.btn_guardar.setText(
            "Guardar",
        )

        self.btn_sincronizar = QPushButton(
            "Sincronizar ahora",
        )

        self.btn_cerrar = Botones.cerrar()

        self.btn_probar.clicked.connect(
            self._probar_conexion,
        )

        self.btn_guardar.clicked.connect(
            self._guardar_configuracion,
        )

        self.btn_sincronizar.clicked.connect(
            self._sincronizar,
        )

        self.btn_cerrar.clicked.connect(
            self.reject,
        )

        barra.addWidget(
            self.btn_probar,
        )

        barra.addStretch()

        barra.addWidget(
            self.btn_guardar,
        )

        barra.addWidget(
            self.btn_sincronizar,
        )

        barra.addWidget(
            self.btn_cerrar,
        )

        layout.addLayout(
            barra,
        )

    def _cargar_configuracion(
        self,
    ) -> None:

        config = self._config()

        endpoints = config.get(
            "endpoints",
        ) or {}

        self.chk_habilitado.setChecked(
            bool(
                config.get(
                    "habilitado",
                    False,
                ),
            ),
        )

        self.txt_url.setText(
            str(
                config.get(
                    "url_base",
                    "",
                )
                or "",
            ),
        )

        self.txt_token.setText(
            str(
                config.get(
                    "token",
                    "",
                )
                or "",
            ),
        )

        nit = str(
            config.get(
                "nit_receptor",
                "",
            )
            or "",
        ).strip()

        if not nit:

            nit = str(
                Configuracion.obtener(
                    "empresa",
                    "nit",
                )
                or "",
            )

        self.txt_nit.setText(
            nit,
        )

        try:

            self.spn_dias.setValue(
                int(
                    config.get(
                        "dias_consulta",
                        30,
                    )
                    or 30,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            pass

        self.chk_auto_cufe.setChecked(
            bool(
                config.get(
                    "auto_validar_cufe",
                    True,
                ),
            ),
        )

        self.chk_modo_automatico.setChecked(
            bool(
                config.get(
                    "modo_automatico",
                    False,
                ),
            ),
        )

        self.chk_sincronizar_inicio.setChecked(
            bool(
                config.get(
                    "sincronizar_al_iniciar",
                    True,
                ),
            ),
        )

        self.chk_sincronizar_compras.setChecked(
            bool(
                config.get(
                    "sincronizar_al_abrir_compras",
                    True,
                ),
            ),
        )

        self.chk_crear_proveedor.setChecked(
            bool(
                config.get(
                    "crear_proveedor_automatico",
                    True,
                ),
            ),
        )

        compras = dict(
            Configuracion.obtener(
                "compras",
            )
            or {},
        )

        self.chk_auto_acuse.setChecked(
            bool(
                config.get(
                    "auto_acuse_recibo_credito",
                    compras.get(
                        "auto_acuse_recibo_credito",
                        True,
                    ),
                ),
            ),
        )

        self.chk_notificar.setChecked(
            bool(
                config.get(
                    "notificar_nuevas",
                    True,
                ),
            ),
        )

        try:

            self.spn_intervalo.setValue(
                int(
                    config.get(
                        "intervalo_minutos",
                        30,
                    )
                    or 30,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            pass

        self.txt_listar.setText(
            str(
                endpoints.get(
                    "listar_recibidos",
                    (
                        "/v1/documents/received?"
                        "page={page}&per_page={per_page}"
                        "&from={fecha_desde}&to={fecha_hasta}"
                        "&receiver_nit={nit_receptor}"
                    ),
                )
                or "",
            ),
        )

        self.txt_descargar.setText(
            str(
                endpoints.get(
                    "descargar_xml",
                    "/v1/documents/{track_id}/xml",
                )
                or "",
            ),
        )

        self.txt_enviar_acuse.setText(
            str(
                endpoints.get(
                    "enviar_acuse_recibo",
                    "/v1/documents/events/acuse-recibo",
                )
                or "",
            ),
        )

    def _guardar_en_config(
        self,
    ) -> None:

        datos = Configuracion.cargar()

        dian = datos.setdefault(
            "dian",
            {},
        )

        recepcion = dian.setdefault(
            "recepcion_compras",
            {},
        )

        recepcion["habilitado"] = (
            self.chk_habilitado.isChecked()
        )

        recepcion["url_base"] = (
            self.txt_url.text().strip()
        )

        recepcion["token"] = (
            self.txt_token.text().strip()
        )

        recepcion["nit_receptor"] = (
            self.txt_nit.text().strip()
        )

        recepcion["dias_consulta"] = (
            self.spn_dias.value()
        )

        recepcion["auto_validar_cufe"] = (
            self.chk_auto_cufe.isChecked()
        )

        recepcion["modo_automatico"] = (
            self.chk_modo_automatico.isChecked()
        )

        recepcion["intervalo_minutos"] = (
            self.spn_intervalo.value()
        )

        recepcion["sincronizar_al_iniciar"] = (
            self.chk_sincronizar_inicio.isChecked()
        )

        recepcion["sincronizar_al_abrir_compras"] = (
            self.chk_sincronizar_compras.isChecked()
        )

        recepcion["crear_proveedor_automatico"] = (
            self.chk_crear_proveedor.isChecked()
        )

        recepcion["auto_acuse_recibo_credito"] = (
            self.chk_auto_acuse.isChecked()
        )

        recepcion["notificar_nuevas"] = (
            self.chk_notificar.isChecked()
        )

        recepcion["modo"] = "api"

        recepcion["endpoints"] = {
            "listar_recibidos": (
                self.txt_listar.text().strip()
            ),
            "descargar_xml": (
                self.txt_descargar.text().strip()
            ),
            "enviar_acuse_recibo": (
                self.txt_enviar_acuse.text().strip()
            ),
        }

        compras = dict(
            datos.get(
                "compras",
            )
            or {},
        )

        compras["auto_acuse_recibo_credito"] = (
            self.chk_auto_acuse.isChecked()
        )

        datos["compras"] = compras

        Configuracion.persistir(
            datos,
        )

        from aplicacion.integraciones.dian.programador_recepcion import (
            ProgramadorRecepcionCompras,
        )

        programador = ProgramadorRecepcionCompras.instancia()

        programador.detener()

        programador.iniciar()

    def _agregar_log(
        self,
        mensaje: str,
    ) -> None:

        self.log.append(
            mensaje,
        )

    def _guardar_configuracion(
        self,
    ) -> None:

        self._guardar_en_config()

        QMessageBox.information(
            self,
            "Configuración",
            "La conexión DIAN quedó guardada.",
        )

    def _probar_conexion(
        self,
    ) -> None:

        self._guardar_en_config()

        resultado = ClienteRecepcionDian.probar_conexion()

        if resultado.exito:

            self._agregar_log(
                resultado.mensaje,
            )

            QMessageBox.information(
                self,
                "Conexión DIAN",
                resultado.mensaje,
            )

            return

        self._agregar_log(
            resultado.error
            or resultado.mensaje,
        )

        QMessageBox.warning(
            self,
            "Conexión DIAN",
            resultado.error
            or resultado.mensaje,
        )

    def _sincronizar(
        self,
    ) -> None:

        self._guardar_en_config()

        self.btn_sincronizar.setEnabled(
            False,
        )

        try:

            resultado = ServicioRecepcionCompras.sincronizar()

        finally:

            self.btn_sincronizar.setEnabled(
                True,
            )

        self._agregar_log(
            resultado.mensaje,
        )

        for error in resultado.errores[:10]:

            self._agregar_log(
                f"Error: {error}",
            )

        if (
            resultado.errores
            and not resultado.importadas
        ):

            QMessageBox.warning(
                self,
                "Sincronización DIAN",
                (
                    f"{resultado.mensaje}\n\n"
                    + "\n".join(
                        resultado.errores[:5],
                    )
                ),
            )

            return

        QMessageBox.information(
            self,
            "Sincronización DIAN",
            resultado.mensaje,
        )

        if resultado.importadas > 0:

            self.accept()
