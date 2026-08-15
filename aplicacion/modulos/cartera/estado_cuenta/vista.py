from __future__ import annotations



from PySide6.QtWidgets import (

    QComboBox,

    QLabel,

    QMessageBox,

    QTableWidgetItem,

)



from aplicacion.framework.lookup import LookupWidget

from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.maestros.terceros.cliente_lookup import (

    ClienteLookup,

)

from aplicacion.maestros.terceros.proveedor_lookup import (

    ProveedorLookup,

)

from aplicacion.modulos.cartera.servicios import (

    ServicioCartera,

)





class CarteraEstadoCuentaPage(InquiryPage):



    titulo = "Estado de cuenta"



    _NOMBRE_EXPORT = "estado_cuenta"



    _COLUMNAS = [

        "Fecha",

        "Documento",

        "Tipo",

        "Débito",

        "Crédito",

        "Saldo",

        "Referencia",

    ]



    def __init__(
        self,
        parent=None,
        *,
        bloquear_tercero: bool = False,
    ):

        self._bloquear_tercero = bloquear_tercero

        super().__init__(
            parent,
        )

        if bloquear_tercero:

            self._aplicar_modo_bloqueado()



    def _aplicar_modo_bloqueado(
        self,
    ) -> None:

        self.tipo.setEnabled(
            False,
        )

        self.lookup_cliente.setEnabled(
            False,
        )

        self.lookup_proveedor.setEnabled(
            False,
        )

        self._btn_consultar.hide()



    def _crear_ui(self) -> None:



        super()._crear_ui()



        self.lbl_resumen = QLabel()



        self.layout_principal.insertWidget(

            1,

            self.lbl_resumen,

        )



    def _crear_filtros(self) -> None:



        self._layout_filtros.addWidget(

            QLabel("Tipo:"),

        )



        self.tipo = QComboBox()



        self.tipo.addItem(

            "Cliente (CxC)",

            "cxc",

        )



        self.tipo.addItem(

            "Proveedor (CxP)",

            "cxp",

        )



        self.tipo.currentIndexChanged.connect(

            self._cambiar_tipo,

        )



        self._layout_filtros.addWidget(

            self.tipo,

        )



        self._layout_filtros.addWidget(

            QLabel("Tercero:"),

        )



        self.lookup_cliente = LookupWidget(

            ClienteLookup(),

            self,

        )



        self.lookup_proveedor = LookupWidget(

            ProveedorLookup(),

            self,

        )



        self.lookup_proveedor.hide()



        self._layout_filtros.addWidget(

            self.lookup_cliente,

            1,

        )



        self._layout_filtros.addWidget(

            self.lookup_proveedor,

            1,

        )

        from PySide6.QtWidgets import QPushButton

        self.btn_pdf = QPushButton(
            "Exportar PDF",
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf_reporte,
        )

        self._layout_filtros.addWidget(
            self.btn_pdf,
        )

        self._resultado_reporte: dict | None = None



    def _cambiar_tipo(self) -> None:



        es_cxc = (

            self.tipo.currentData()

            == "cxc"

        )



        self.lookup_cliente.setVisible(

            es_cxc,

        )



        self.lookup_proveedor.setVisible(

            not es_cxc,

        )



    def consultar_cliente_cxc(
        self,
        tercero_id: int,
    ) -> None:

        indice_cxc = self.tipo.findData(
            "cxc",
        )

        if indice_cxc >= 0:

            self.tipo.setCurrentIndex(
                indice_cxc,
            )

        self._cambiar_tipo()
        self.lookup_cliente.setValue(
            tercero_id,
        )

        if self.lookup_cliente.valor() is None:

            self._consultar_cxc_directo(
                tercero_id,
            )

            return

        self._consultar()



    def _consultar_cxc_directo(
        self,
        tercero_id: int,
    ) -> None:

        try:

            resultado = ServicioCartera.estado_cuenta_cxc(
                tercero_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Estado de cuenta",
                str(
                    error,
                ),
            )

            return

        self._mostrar_resultado(
            resultado,
        )



    def _mostrar_resultado(
        self,
        resultado: dict,
    ) -> None:

        self._resultado_reporte = resultado

        self.lbl_resumen.setText(

            f"{resultado['tercero']} · "

            f"Saldo final: "

            f"{resultado['saldo_final']:,.2f}",

        )



        movimientos = resultado[

            "movimientos"

        ]



        self.tabla.setRowCount(

            len(movimientos),

        )



        for i, mov in enumerate(

            movimientos,

        ):



            self.tabla.setItem(

                i,

                0,

                QTableWidgetItem(

                    str(mov["fecha"]),

                ),

            )



            self.tabla.setItem(

                i,

                1,

                QTableWidgetItem(

                    mov["documento"],

                ),

            )



            self.tabla.setItem(

                i,

                2,

                QTableWidgetItem(

                    mov["tipo"],

                ),

            )



            self.tabla.setItem(

                i,

                3,

                QTableWidgetItem(

                    f"{mov['debito']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                4,

                QTableWidgetItem(

                    f"{mov['credito']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                5,

                QTableWidgetItem(

                    f"{mov['saldo']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                6,

                QTableWidgetItem(

                    mov["referencia"],

                ),

            )



        self.tabla.resizeColumnsToContents()



    def _consultar(self) -> None:



        if self.tipo.currentData() == "cxc":



            tercero_id = (

                self.lookup_cliente.valor()

            )



            if tercero_id is None:



                QMessageBox.warning(

                    self,

                    "Estado de cuenta",

                    "Seleccione un cliente.",

                )



                return



            try:



                resultado = (

                    ServicioCartera.estado_cuenta_cxc(

                        tercero_id,

                    )

                )



            except ValueError as error:



                QMessageBox.warning(

                    self,

                    "Estado de cuenta",

                    str(error),

                )



                return



        else:



            tercero_id = (

                self.lookup_proveedor.valor()

            )



            if tercero_id is None:



                QMessageBox.warning(

                    self,

                    "Estado de cuenta",

                    "Seleccione un proveedor.",

                )



                return



            try:



                resultado = (

                    ServicioCartera.estado_cuenta_cxp(

                        tercero_id,

                    )

                )



            except ValueError as error:



                QMessageBox.warning(

                    self,

                    "Estado de cuenta",

                    str(error),

                )



                return



        self._mostrar_resultado(
            resultado,
        )

    def _exportar_pdf_reporte(
        self,
    ) -> None:

        if not getattr(
            self,
            "_resultado_reporte",
            None,
        ):

            self._consultar()

        if not self._resultado_reporte:

            return

        from aplicacion.framework.reportes.impresion_util import (
            abrir_centro_impresion,
        )
        from aplicacion.reportes.cartera.estado_cuenta import (
            crear_reporte_estado_cuenta_cxc,
            crear_reporte_estado_cuenta_cxp,
        )

        if self.tipo.currentData() == "cxc":

            reporte = crear_reporte_estado_cuenta_cxc(
                self._resultado_reporte,
            )

        else:

            reporte = crear_reporte_estado_cuenta_cxp(
                self._resultado_reporte,
            )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )

