from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.integraciones.dian.go_live import ValidadorGoLiveDian
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.ui.botones import Botones


class ConfiguracionDianPage(Page):

    titulo = "Configuración DIAN"

    def _crear_ui(self):

        super()._crear_ui()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)

        layout.addWidget(
            self._crear_grupo_ambiente(),
        )
        layout.addWidget(
            self._crear_grupo_certificado(),
        )
        layout.addWidget(
            self._crear_grupo_resolucion(),
        )
        layout.addWidget(
            self._crear_grupo_almacenamiento(),
        )

        botones = QHBoxLayout()

        self.btn_guardar = Botones.guardar()
        self.btn_guardar.clicked.connect(
            self._guardar,
        )

        self.btn_verificar_habilitacion = QPushButton(
            "Verificar habilitación",
        )
        self.btn_verificar_habilitacion.clicked.connect(
            lambda: self._verificar("habilitacion"),
        )

        self.btn_verificar_produccion = QPushButton(
            "Verificar producción",
        )
        self.btn_verificar_produccion.clicked.connect(
            lambda: self._verificar("produccion"),
        )

        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_verificar_habilitacion)
        botones.addWidget(self.btn_verificar_produccion)
        botones.addStretch()

        layout.addLayout(botones)

        self.resultado_verificacion = QTextEdit()
        self.resultado_verificacion.setReadOnly(True)
        self.resultado_verificacion.setPlaceholderText(
            "El resultado de la verificación de go-live "
            "aparecerá aquí.",
        )
        self.resultado_verificacion.setMinimumHeight(140)

        layout.addWidget(
            self.resultado_verificacion,
        )

        scroll.setWidget(contenedor)

        self.agregar_widget(scroll)

        self._cargar_datos()

    # =====================================================
    # Grupos de campos
    # =====================================================

    def _crear_grupo_ambiente(self) -> QGroupBox:

        grupo = QGroupBox("Ambiente")
        formulario = QFormLayout(grupo)

        self.emision_habilitada = QCheckBox(
            "Emisión electrónica habilitada",
        )

        self.ambiente_emision = QComboBox()
        self.ambiente_emision.addItem(
            "Habilitación (pruebas)",
            "habilitacion",
        )
        self.ambiente_emision.addItem(
            "Producción",
            "produccion",
        )

        self.prefijo_factura = QLineEdit()
        self.test_set_id = QLineEdit()
        self.software_id = QLineEdit()
        self.software_pin = QLineEdit()
        self.software_pin.setEchoMode(
            QLineEdit.EchoMode.Password,
        )

        formulario.addRow(
            "",
            self.emision_habilitada,
        )
        formulario.addRow(
            "Ambiente",
            self.ambiente_emision,
        )
        formulario.addRow(
            "Prefijo factura",
            self.prefijo_factura,
        )
        formulario.addRow(
            "Test set ID (habilitación)",
            self.test_set_id,
        )
        formulario.addRow(
            "Software ID",
            self.software_id,
        )
        formulario.addRow(
            "Software PIN",
            self.software_pin,
        )

        return grupo

    def _crear_grupo_certificado(self) -> QGroupBox:

        grupo = QGroupBox("Certificado digital")
        formulario = QFormLayout(grupo)

        fila_ruta = QHBoxLayout()

        self.certificado_ruta = QLineEdit()

        btn_examinar = QPushButton("Examinar…")
        btn_examinar.clicked.connect(
            self._seleccionar_certificado,
        )

        fila_ruta.addWidget(self.certificado_ruta)
        fila_ruta.addWidget(btn_examinar)

        self.certificado_clave = QLineEdit()
        self.certificado_clave.setEchoMode(
            QLineEdit.EchoMode.Password,
        )

        formulario.addRow(
            "Archivo (.p12/.pfx)",
            fila_ruta,
        )
        formulario.addRow(
            "Contraseña",
            self.certificado_clave,
        )

        return grupo

    def _crear_grupo_resolucion(self) -> QGroupBox:

        grupo = QGroupBox("Resolución de facturación")
        formulario = QFormLayout(grupo)

        self.resolucion_numero = QLineEdit()

        self.resolucion_fecha_inicio = QDateEdit()
        self.resolucion_fecha_inicio.setCalendarPopup(True)
        self.resolucion_fecha_inicio.setDisplayFormat(
            "yyyy-MM-dd",
        )

        self.resolucion_fecha_fin = QDateEdit()
        self.resolucion_fecha_fin.setCalendarPopup(True)
        self.resolucion_fecha_fin.setDisplayFormat(
            "yyyy-MM-dd",
        )

        self.resolucion_desde = QLineEdit()
        self.resolucion_hasta = QLineEdit()

        formulario.addRow(
            "Número de resolución",
            self.resolucion_numero,
        )
        formulario.addRow(
            "Vigente desde",
            self.resolucion_fecha_inicio,
        )
        formulario.addRow(
            "Vigente hasta",
            self.resolucion_fecha_fin,
        )
        formulario.addRow(
            "Consecutivo desde",
            self.resolucion_desde,
        )
        formulario.addRow(
            "Consecutivo hasta",
            self.resolucion_hasta,
        )

        return grupo

    def _crear_grupo_almacenamiento(self) -> QGroupBox:

        grupo = QGroupBox("Almacenamiento de documentos")
        formulario = QFormLayout(grupo)

        fila_carpeta = QHBoxLayout()

        self.carpeta_xml_venta = QLineEdit()

        btn_carpeta = QPushButton("Examinar…")
        btn_carpeta.clicked.connect(
            self._seleccionar_carpeta,
        )

        fila_carpeta.addWidget(self.carpeta_xml_venta)
        fila_carpeta.addWidget(btn_carpeta)

        self.contenedor_incluir_pdf = QCheckBox(
            "Incluir representación gráfica (PDF) en el ZIP",
        )

        formulario.addRow(
            "Carpeta XML/ZIP",
            fila_carpeta,
        )
        formulario.addRow(
            "",
            self.contenedor_incluir_pdf,
        )

        return grupo

    # =====================================================
    # Diálogos auxiliares
    # =====================================================

    def _seleccionar_certificado(self):

        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar certificado digital",
            "",
            "Certificados (*.p12 *.pfx)",
        )

        if archivo:

            self.certificado_ruta.setText(archivo)

    def _seleccionar_carpeta(self):

        carpeta = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de almacenamiento",
        )

        if carpeta:

            self.carpeta_xml_venta.setText(carpeta)

    # =====================================================
    # Carga / guardado
    # =====================================================

    def _fecha_a_qdate(
        self,
        valor: str | None,
    ) -> QDate:

        if valor:

            try:

                fecha = date.fromisoformat(
                    str(valor),
                )

                return QDate(
                    fecha.year,
                    fecha.month,
                    fecha.day,
                )

            except ValueError:

                pass

        return QDate.currentDate()

    def _cargar_datos(self):

        obtener = Configuracion.obtener

        self.emision_habilitada.setChecked(
            bool(
                obtener("dian", "emision_habilitada"),
            ),
        )

        indice = self.ambiente_emision.findData(
            str(
                obtener("dian", "ambiente_emision")
                or "habilitacion",
            ),
        )

        if indice >= 0:

            self.ambiente_emision.setCurrentIndex(
                indice,
            )

        self.prefijo_factura.setText(
            str(obtener("dian", "prefijo_factura") or ""),
        )
        self.test_set_id.setText(
            str(obtener("dian", "test_set_id") or ""),
        )
        self.software_id.setText(
            str(obtener("dian", "software_id") or ""),
        )
        self.software_pin.setText(
            str(obtener("dian", "software_pin") or ""),
        )
        self.certificado_ruta.setText(
            str(obtener("dian", "certificado_ruta") or ""),
        )
        self.certificado_clave.setText(
            str(obtener("dian", "certificado_clave") or ""),
        )
        self.resolucion_numero.setText(
            str(obtener("dian", "resolucion_numero") or ""),
        )

        self.resolucion_fecha_inicio.setDate(
            self._fecha_a_qdate(
                obtener("dian", "resolucion_fecha_inicio"),
            ),
        )
        self.resolucion_fecha_fin.setDate(
            self._fecha_a_qdate(
                obtener("dian", "resolucion_fecha_fin"),
            ),
        )

        self.resolucion_desde.setText(
            str(obtener("dian", "resolucion_desde") or ""),
        )
        self.resolucion_hasta.setText(
            str(obtener("dian", "resolucion_hasta") or ""),
        )
        self.carpeta_xml_venta.setText(
            str(obtener("dian", "carpeta_xml_venta") or ""),
        )
        self.contenedor_incluir_pdf.setChecked(
            bool(
                obtener("dian", "contenedor_incluir_pdf"),
            ),
        )

    def _guardar(self):

        try:

            actualizar = Configuracion.actualizar

            actualizar(
                ("dian", "emision_habilitada"),
                self.emision_habilitada.isChecked(),
            )
            actualizar(
                ("dian", "ambiente_emision"),
                self.ambiente_emision.currentData(),
            )
            actualizar(
                ("dian", "prefijo_factura"),
                self.prefijo_factura.text().strip().upper(),
            )
            actualizar(
                ("dian", "test_set_id"),
                self.test_set_id.text().strip(),
            )
            actualizar(
                ("dian", "software_id"),
                self.software_id.text().strip(),
            )
            actualizar(
                ("dian", "software_pin"),
                self.software_pin.text().strip(),
            )
            actualizar(
                ("dian", "certificado_ruta"),
                self.certificado_ruta.text().strip(),
            )
            actualizar(
                ("dian", "certificado_clave"),
                self.certificado_clave.text(),
            )
            actualizar(
                ("dian", "resolucion_numero"),
                self.resolucion_numero.text().strip(),
            )
            actualizar(
                ("dian", "resolucion_fecha_inicio"),
                self.resolucion_fecha_inicio.date().toString(
                    "yyyy-MM-dd",
                ),
            )
            actualizar(
                ("dian", "resolucion_fecha_fin"),
                self.resolucion_fecha_fin.date().toString(
                    "yyyy-MM-dd",
                ),
            )
            actualizar(
                ("dian", "resolucion_desde"),
                self.resolucion_desde.text().strip(),
            )
            actualizar(
                ("dian", "resolucion_hasta"),
                self.resolucion_hasta.text().strip(),
            )
            actualizar(
                ("dian", "carpeta_xml_venta"),
                self.carpeta_xml_venta.text().strip(),
            )
            actualizar(
                ("dian", "contenedor_incluir_pdf"),
                self.contenedor_incluir_pdf.isChecked(),
            )

        except OSError as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la configuración: {error}",
            )

            return

        QMessageBox.information(
            self,
            "Configuración DIAN",
            "Configuración guardada correctamente.",
        )

    def _verificar(
        self,
        ambiente: str,
    ):

        self._guardar()

        resultado = ValidadorGoLiveDian.verificar(
            ambiente_objetivo=ambiente,
        )

        self.resultado_verificacion.setPlainText(
            ValidadorGoLiveDian.resumen_texto(
                resultado,
            ),
        )
