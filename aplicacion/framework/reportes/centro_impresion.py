from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.reportes.documento_pdf import (
    DocumentoPdf,
)
from aplicacion.recursos.ui.botones import Botones


class CentroImpresionDialog(
    QDialog,
):

    def __init__(
        self,
        documento: DocumentoPdf,
        *,
        parent: QWidget | None = None,
        titulo: str | None = None,
    ):

        super().__init__(
            parent,
        )

        self.documento = documento

        self.setWindowTitle(
            titulo
            or documento.reporte.titulo_documento,
        )

        self.resize(
            920,
            760,
        )

        self._construir()

    def _construir(
        self,
    ) -> None:

        layout = QVBoxLayout(
            self,
        )

        encabezado = QHBoxLayout()

        encabezado.addWidget(
            QLabel(
                f"Documento: {self.documento.reporte.numero_documento}",
            ),
        )

        encabezado.addStretch()

        encabezado.addWidget(
            QLabel(
                "Formato:",
            ),
        )

        self.cmb_formato = QComboBox()

        for etiqueta, codigo in (
            self.documento.reporte.formatos_pagina_disponibles()
        ):

            self.cmb_formato.addItem(
                etiqueta,
                codigo,
            )

        predeterminado = (
            self.documento.reporte.formato_pagina_predeterminado()
        )

        indice = self.cmb_formato.findData(
            predeterminado,
        )

        if indice >= 0:

            self.cmb_formato.setCurrentIndex(
                indice,
            )

        encabezado.addWidget(
            self.cmb_formato,
        )

        layout.addLayout(
            encabezado,
        )

        self.vista = QTextBrowser()

        self.vista.setOpenExternalLinks(
            True,
        )

        self.vista.setHtml(
            self.documento.html,
        )

        layout.addWidget(
            self.vista,
            1,
        )

        acciones = QHBoxLayout()

        btn_imprimir = Botones.primario()

        btn_imprimir.setText(
            "Imprimir",
        )

        btn_imprimir.clicked.connect(
            self._imprimir,
        )

        btn_pdf = Botones.secundario()

        btn_pdf.setText(
            "Exportar PDF",
        )

        btn_pdf.clicked.connect(
            self._exportar_pdf,
        )

        btn_correo = Botones.secundario()

        btn_correo.setText(
            "Enviar correo",
        )

        btn_correo.clicked.connect(
            self._enviar_correo,
        )

        btn_whatsapp = Botones.secundario()

        btn_whatsapp.setText(
            "WhatsApp",
        )

        btn_whatsapp.clicked.connect(
            self._enviar_whatsapp,
        )

        btn_cerrar = QPushButton(
            "Cerrar",
        )

        btn_cerrar.clicked.connect(
            self.reject,
        )

        acciones.addWidget(
            btn_imprimir,
        )

        acciones.addWidget(
            btn_pdf,
        )

        acciones.addWidget(
            btn_correo,
        )

        acciones.addWidget(
            btn_whatsapp,
        )

        acciones.addStretch()

        acciones.addWidget(
            btn_cerrar,
        )

        layout.addLayout(
            acciones,
        )

    def _formato_actual(
        self,
    ) -> str:

        return str(
            self.cmb_formato.currentData()
            or "carta",
        )

    def _imprimir(
        self,
    ) -> None:

        self.documento.imprimir(
            parent=self,
            formato_pagina=self._formato_actual(),
        )

    def _exportar_pdf(
        self,
    ) -> None:

        from PySide6.QtWidgets import (
            QFileDialog,
        )

        ruta, _filtro = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            self.documento.reporte.nombre_archivo_pdf(),
            "PDF (*.pdf)",
        )

        if not ruta:

            return

        if not ruta.lower().endswith(
            ".pdf",
        ):

            ruta = f"{ruta}.pdf"

        self.documento.exportar_pdf(
            ruta,
            formato_pagina=self._formato_actual(),
        )

    def _enviar_correo(
        self,
    ) -> None:

        from aplicacion.framework.reportes.envio_documento import (
            enviar_documento_correo,
        )

        enviar_documento_correo(
            self.documento,
            parent=self,
            formato_pagina=self._formato_actual(),
        )

    def _enviar_whatsapp(
        self,
    ) -> None:

        from aplicacion.framework.reportes.envio_documento import (
            enviar_documento_whatsapp,
        )

        enviar_documento_whatsapp(
            self.documento,
            parent=self,
        )
