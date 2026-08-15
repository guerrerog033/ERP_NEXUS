from __future__ import annotations



from PySide6.QtPrintSupport import QPrintDialog, QPrinter

from PySide6.QtWidgets import (

    QDialog,

    QFileDialog,

    QInputDialog,

    QMessageBox,

    QTableWidget,

    QTableWidgetItem,

    QVBoxLayout,

)



from aplicacion.framework.ui.vista_documento import (

    VistaDocumento,

)

from aplicacion.maestros.terceros.servicio import (

    TerceroServicio,

)

from aplicacion.modulos.compras.facturas.datasource import (

    FacturaCompraDataSource,

)

from aplicacion.modulos.compras.facturas.formatos_impresion import (

    generar_html_factura_compra,

)

from aplicacion.modulos.compras.facturas.impresion import (

    exportar_pdf_factura_compra,

    imprimir_factura_compra,

)

from aplicacion.modulos.compras.integracion_oc import (
    ServicioIntegracionCompras,
)

from aplicacion.recursos.ui.botones import Botones





class VistaFacturaCompra(VistaDocumento):



    def __init__(

        self,

        id_registro: int,

        parent=None,

    ):



        self.datasource = FacturaCompraDataSource()



        self._factura = None

        self._detalles: list = []

        self._nombre_proveedor = ""

        self._proveedor = None



        super().__init__(

            id_registro,

            parent=parent,

        )



    def _agregar_barras_accion(

        self,

    ) -> None:



        self.btn_validar_cufe = self.boton_accion(

            "Validar CUFE DIAN",

        )



        self.btn_contabilizar = self.boton_accion(

            "Contabilizar",

        )

        self.btn_nota_credito = self.boton_accion(
            "Nota crédito compra",
        )

        self.btn_vincular_oc = self.boton_accion(
            "Vincular OC",
        )

        self.btn_evaluar_match = self.boton_accion(
            "Evaluar match",
        )

        self.btn_aprobar = self.boton_accion(

            "Aprobar revisión",

        )

        self.btn_acuse_recibo = self.boton_accion(

            "Enviar acuse de recibo",

        )

        self.btn_radian_031 = self.boton_accion(
            "RADIAN 031",
        )

        self.btn_radian_032 = self.boton_accion(
            "RADIAN 032",
        )

        self.btn_radian_033 = self.boton_accion(
            "RADIAN 033",
        )

        self.btn_radian_034 = self.boton_accion(
            "RADIAN 034",
        )

        self.btn_historial_radian = self.boton_accion(
            "Historial RADIAN",
        )



        self.layout_principal.addLayout(

            self._barra_etiquetada(

                "Integración",

                (

                    self.btn_aprobar,

                    self.btn_vincular_oc,

                    self.btn_evaluar_match,

                    self.btn_acuse_recibo,

                    self.btn_validar_cufe,

                    self.btn_contabilizar,

                    self.btn_nota_credito,

                ),

            ),

        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Eventos RADIAN",
                (
                    self.btn_radian_031,
                    self.btn_radian_032,
                    self.btn_radian_033,
                    self.btn_radian_034,
                    self.btn_historial_radian,
                ),
            ),
        )



        self.btn_editar = Botones.editar()



        self.btn_imprimir = Botones.editar()



        self.btn_imprimir.setText(

            "Imprimir",

        )



        self.btn_pdf = Botones.aceptar()



        self.btn_pdf.setText(

            "PDF",

        )



        self.btn_cerrar = Botones.cerrar()



        self.layout_principal.addLayout(

            self._barra_etiquetada(

                self.etiqueta_barra_principal(),

                (

                    self.btn_editar,

                    self.btn_imprimir,

                    self.btn_pdf,

                    self.btn_cerrar,

                ),

                separar_ultimo=True,

            ),

        )



    def _conectar_acciones(

        self,

    ) -> None:



        self.btn_editar.clicked.connect(

            self.editar_solicitado.emit,

        )



        self.btn_imprimir.clicked.connect(

            self._imprimir,

        )



        self.btn_pdf.clicked.connect(

            self._exportar_pdf,

        )



        self.btn_cerrar.clicked.connect(

            self.cerrar.emit,

        )



        self.btn_validar_cufe.clicked.connect(

            self._validar_cufe,

        )



        self.btn_contabilizar.clicked.connect(

            self._contabilizar,

        )

        self.btn_nota_credito.clicked.connect(
            self._crear_nota_credito_compra,
        )

        self.btn_vincular_oc.clicked.connect(
            self._vincular_orden_compra,
        )

        self.btn_evaluar_match.clicked.connect(
            self._evaluar_match_oc,
        )

        self.btn_aprobar.clicked.connect(

            self._aprobar_revision,

        )

        self.btn_acuse_recibo.clicked.connect(

            self._enviar_acuse_recibo,

        )

        self.btn_radian_031.clicked.connect(
            lambda: self._enviar_evento_radian(
                "031",
            ),
        )

        self.btn_radian_032.clicked.connect(
            lambda: self._enviar_evento_radian(
                "032",
            ),
        )

        self.btn_radian_033.clicked.connect(
            lambda: self._enviar_evento_radian(
                "033",
            ),
        )

        self.btn_radian_034.clicked.connect(
            lambda: self._enviar_evento_radian(
                "034",
            ),
        )

        self.btn_historial_radian.clicked.connect(
            self._mostrar_historial_radian,
        )



    def etiqueta_barra_principal(

        self,

    ) -> str:



        return "Factura compra"



    def _etiqueta_estado(

        self,

    ) -> str:



        if self._factura is None:



            return ""



        partes = [

            self._factura.origen.upper(),

            self._factura.estado,

        ]



        if self._factura.cufe:



            if self._factura.cufe_validado:



                partes.append(

                    "CUFE validado",

                )



            else:



                partes.append(

                    "CUFE sin validar",

                )



        if self._factura.contabilizado:



            partes.append(

                "Contabilizada",

            )



        if self._factura.requiere_acuse_recibo:

            estado_acuse = (
                self._factura.acuse_recibo_estado
                or "pendiente"
            )

            partes.append(
                f"Acuse: {estado_acuse}",
            )

        elif self._factura.es_credito:

            partes.append(
                "Credito",
            )

        if self._factura.evento_radian_codigo:

            partes.append(
                "RADIAN "
                f"{self._factura.evento_radian_codigo}",
            )

        if self._factura.orden_compra_id:

            partes.append(
                f"OC #{self._factura.orden_compra_id}",
            )

        if self._factura.match_estado:

            partes.append(
                f"Match: {self._factura.match_estado}",
            )

        return " · ".join(partes)



    def _actualizar_botones(

        self,

    ) -> None:



        if self._factura is None:



            return



        tiene_cufe = bool(

            self._factura.cufe,

        )



        self.btn_validar_cufe.setEnabled(

            tiene_cufe

            and not self._factura.contabilizado

            and self._factura.estado
            != "pendiente_revision",

        )

        pendiente = (
            self._factura.estado
            == "pendiente_revision"
        )

        self.btn_aprobar.setVisible(
            pendiente,
        )

        self.btn_aprobar.setEnabled(
            pendiente,
        )

        self.btn_contabilizar.setEnabled(

            not self._factura.contabilizado

            and not pendiente,

        )

        self.btn_nota_credito.setEnabled(
            self._factura.contabilizado,
        )

        puede_vincular = (
            not self._factura.contabilizado
        )

        self.btn_vincular_oc.setEnabled(
            puede_vincular,
        )

        self.btn_evaluar_match.setEnabled(
            bool(
                self._factura.orden_compra_id,
            )
            and not self._factura.contabilizado,
        )

        requiere_acuse = bool(
            self._factura.requiere_acuse_recibo,
        )

        acuse_ok = (
            self._factura.acuse_recibo_estado
            in (
                "enviado",
                "aceptado",
            )
        )

        self.btn_acuse_recibo.setVisible(
            requiere_acuse,
        )

        self.btn_acuse_recibo.setEnabled(
            requiere_acuse,
        )

        self.btn_acuse_recibo.setText(
            "Reenviar acuse de recibo"
            if acuse_ok
            else "Enviar acuse de recibo",
        )

        tiene_cufe_radian = bool(
            self._factura.cufe,
        )

        for boton in (
            self.btn_radian_031,
            self.btn_radian_032,
            self.btn_radian_033,
            self.btn_radian_034,
        ):

            boton.setEnabled(
                tiene_cufe_radian
                and not pendiente,
            )



    def _validar_cufe(

        self,

    ) -> None:



        try:



            resultado = (

                self.datasource.validar_cufe_online(

                    self.id_registro,

                )

            )



        except ValueError as error:



            QMessageBox.warning(

                self,

                "Validar CUFE",

                str(error),

            )



            return



        if resultado.valido:



            QMessageBox.information(

                self,

                "Validar CUFE",

                resultado.mensaje

                or "CUFE validado en DIAN.",

            )



        else:



            QMessageBox.warning(

                self,

                "Validar CUFE",

                resultado.mensaje

                or resultado.error

                or "El CUFE no fue validado.",

            )



        self._cargar_datos()

        self.actualizado.emit()



    def _aprobar_revision(

        self,

    ) -> None:

        try:

            estado = self.datasource.aprobar_revision(

                self.id_registro,

            )

        except ValueError as error:

            QMessageBox.warning(

                self,

                "Aprobar revisión",

                str(error),

            )

            return

        QMessageBox.information(

            self,

            "Aprobar revisión",

            (
                "Factura aprobada. Estado actual: "
                f"{estado}."
            ),

        )

        self._cargar_datos()

        self.actualizado.emit()



    def _enviar_acuse_recibo(

        self,

    ) -> None:

        acuse_ok = (
            self._factura
            and self._factura.acuse_recibo_estado
            in (
                "enviado",
                "aceptado",
            )
        )

        if acuse_ok:

            confirmar = QMessageBox.question(

                self,

                "Acuse de recibo",

                "El acuse ya fue registrado. "
                "Desea reenviarlo?",

                QMessageBox.StandardButton.Yes

                | QMessageBox.StandardButton.No,

            )

            if (
                confirmar
                != QMessageBox.StandardButton.Yes
            ):

                return

        try:

            resultado = (
                self.datasource.generar_acuse_recibo(
                    self.id_registro,
                    forzar=acuse_ok,
                )
            )

        except ValueError as error:

            QMessageBox.warning(

                self,

                "Acuse de recibo",

                str(error),

            )

            return

        if resultado.exito:

            QMessageBox.information(

                self,

                "Acuse de recibo",

                resultado.mensaje

                or "Acuse de recibo enviado.",

            )

        else:

            QMessageBox.warning(

                self,

                "Acuse de recibo",

                resultado.error

                or resultado.mensaje

                or "No se pudo enviar el acuse.",

            )

        self._cargar_datos()

        self.actualizado.emit()

    def _enviar_evento_radian(
        self,
        codigo_evento: str,
    ) -> None:

        from aplicacion.integraciones.dian.generador_acuse_recibo import (
            GeneradorAcuseRecibo,
        )
        from aplicacion.integraciones.dian.servicio_eventos_radian import (
            ServicioEventosRadian,
        )

        descripcion = GeneradorAcuseRecibo.descripcion_evento(
            codigo_evento,
        )

        if (
            self._factura
            and self._factura.evento_radian_codigo
            == codigo_evento
        ):

            confirmar = QMessageBox.question(
                self,
                f"RADIAN {codigo_evento}",
                (
                    f"El evento {codigo_evento} ya fue "
                    "registrado. ¿Desea reenviarlo?"
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
            )

            if (
                confirmar
                != QMessageBox.StandardButton.Yes
            ):

                return

        try:

            resultado = ServicioEventosRadian.procesar(
                self.id_registro,
                codigo_evento,
                forzar=(
                    self._factura is not None
                    and self._factura.evento_radian_codigo
                    == codigo_evento
                ),
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                f"RADIAN {codigo_evento}",
                str(error),
            )

            return

        titulo = f"RADIAN {codigo_evento}"

        if resultado.exito:

            QMessageBox.information(
                self,
                titulo,
                resultado.mensaje or descripcion,
            )

        else:

            QMessageBox.warning(
                self,
                titulo,
                resultado.error
                or resultado.mensaje
                or "No se pudo registrar el evento.",
            )

        self._cargar_datos()

        self.actualizado.emit()

    def _mostrar_historial_radian(
        self,
    ) -> None:

        from aplicacion.modulos.compras.facturas.repositorio_eventos_radian import (
            RepositorioFacturaCompraEventoRadian,
        )

        eventos = (
            RepositorioFacturaCompraEventoRadian
            .listar_por_factura(
                self.id_registro,
            )
        )

        dialogo = QDialog(
            self,
        )

        dialogo.setWindowTitle(
            "Historial eventos RADIAN",
        )

        dialogo.resize(
            920,
            420,
        )

        layout = QVBoxLayout(
            dialogo,
        )

        tabla = QTableWidget()

        tabla.setColumnCount(6)

        tabla.setHorizontalHeaderLabels(
            [
                "Fecha",
                "Evento",
                "Estado",
                "CUDE",
                "Mensaje",
                "Forzado",
            ],
        )

        tabla.setRowCount(
            len(eventos),
        )

        for indice, evento in enumerate(
            eventos,
        ):

            valores = [
                str(
                    evento.fecha_evento
                    or "",
                ),
                evento.codigo_evento,
                evento.estado,
                evento.cude or "",
                evento.mensaje or "",
                "Sí" if evento.forzado else "No",
            ]

            for columna, valor in enumerate(
                valores,
            ):

                tabla.setItem(
                    indice,
                    columna,
                    QTableWidgetItem(
                        str(valor),
                    ),
                )

        tabla.resizeColumnsToContents()

        layout.addWidget(
            tabla,
        )

        dialogo.exec()

    def _crear_nota_credito_compra(
        self,
    ) -> None:

        from aplicacion.modulos.compras.notas_credito.servicios import (
            ServicioNotaCreditoCompra,
        )
        from aplicacion.modulos.compras.notas_credito.vista import (
            VistaNotaCreditoCompra,
        )

        confirmar = QMessageBox.question(
            self,
            "Nota crédito compra",
            "Se creará una nota crédito con las "
            "mismas líneas de esta factura "
            "(devolución al proveedor). "
            "¿Desea continuar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            confirmar
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            nota = (
                ServicioNotaCreditoCompra
                .crear_desde_factura(
                    self.id_registro,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Nota crédito compra",
                str(error),
            )

            return

        ventana = QDialog(
            self,
        )

        ventana.setWindowTitle(
            f"NC compra {nota.numero}",
        )

        ventana.setModal(
            True,
        )

        ventana.resize(
            1120,
            720,
        )

        layout = QVBoxLayout(
            ventana,
        )

        vista = VistaNotaCreditoCompra(
            id_registro=nota.id,
            parent=ventana,
        )

        layout.addWidget(
            vista,
        )

        vista.cerrar.connect(
            ventana.accept,
        )

        ventana.exec()

        vista.deleteLater()

    def _vincular_orden_compra(
        self,
    ) -> None:

        if self._factura is None:

            return

        sugerencias = ServicioIntegracionCompras.sugerir_ordenes(
            self.id_registro,
        )

        if not sugerencias:

            QMessageBox.information(
                self,
                "Vincular OC",
                "No hay órdenes de compra "
                "sugeridas para este proveedor.",
            )

            return

        etiquetas = [
            (
                f"{item['numero']} — "
                f"{item['fecha']} — "
                f"${item['total']:,.0f} "
                f"({item['estado']})"
            )
            for item in sugerencias
        ]

        seleccion, ok = QInputDialog.getItem(
            self,
            "Vincular orden de compra",
            "Seleccione la OC:",
            etiquetas,
            0,
            False,
        )

        if not ok:

            return

        indice = etiquetas.index(
            seleccion,
        )

        orden_id = sugerencias[indice]["id"]

        try:

            resultado = (
                ServicioIntegracionCompras.vincular_orden(
                    self.id_registro,
                    orden_id,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Vincular OC",
                str(error),
            )

            return

        mensaje = resultado.mensaje

        if resultado.diferencias:

            mensaje += "\n\n" + "\n".join(
                resultado.diferencias[:8],
            )

        QMessageBox.information(
            self,
            "Vincular OC",
            mensaje,
        )

        self._cargar_datos()

        self.actualizado.emit()

    def _evaluar_match_oc(
        self,
    ) -> None:

        if self._factura is None:

            return

        resultado = ServicioIntegracionCompras.evaluar_match(
            self.id_registro,
            persistir=True,
        )

        mensaje = resultado.mensaje

        if resultado.diferencias:

            mensaje += "\n\n" + "\n".join(
                resultado.diferencias[:12],
            )

        QMessageBox.information(
            self,
            "Match OC",
            mensaje,
        )

        self._cargar_datos()

        self.actualizado.emit()

    def _contabilizar(

        self,

    ) -> None:



        confirmar = QMessageBox.question(

            self,

            "Contabilizar",

            "Se registrará el asiento contable. "

            "Las entradas de inventario omiten "

            "líneas ya recibidas por OC. "

            "¿Desea continuar?",

            QMessageBox.StandardButton.Yes

            | QMessageBox.StandardButton.No,

        )



        if (

            confirmar

            != QMessageBox.StandardButton.Yes

        ):



            return



        try:



            asiento = self.datasource.contabilizar(

                self.id_registro,

            )



        except ValueError as error:



            QMessageBox.warning(

                self,

                "Contabilizar",

                str(error),

            )



            return



        QMessageBox.information(

            self,

            "Contabilizar",

            f"Asiento {asiento.numero} registrado. "

            "Inventario actualizado.",

        )



        self._cargar_datos()

        self.actualizado.emit()



    def _cargar_datos(

        self,

    ) -> None:



        factura = self.datasource.obtener_completa(

            self.id_registro,

        )



        if factura is None:



            QMessageBox.warning(

                self,

                "Factura de compra",

                "No se encontró la factura seleccionada.",

            )



            self.cerrar.emit()



            return



        nombre_proveedor = (

            factura.razon_social_proveedor

            or ""

        )



        proveedor = None

        if factura.proveedor_id:



            proveedor = TerceroServicio.obtener_por_id(

                factura.proveedor_id,

            )



            if proveedor is not None:



                nombre_proveedor = (

                    proveedor.razon_social

                    or proveedor.nombre_completo

                    or proveedor.numero_documento

                    or nombre_proveedor

                )



        if (

            not nombre_proveedor

            and factura.nit_proveedor

        ):



            nombre_proveedor = (

                f"NIT {factura.nit_proveedor}"

            )



        self._factura = factura

        self._detalles = list(

            factura.detalles,

        )

        self._nombre_proveedor = nombre_proveedor

        self._proveedor = proveedor



        titulo = f"Factura {factura.numero}"



        if nombre_proveedor:



            titulo += f" — {nombre_proveedor}"



        self.lbl_titulo.setText(

            titulo,

        )



        self.mostrar_formato(

            self._etiqueta_estado(),

        )



        self.establecer_html(

            generar_html_factura_compra(

                factura,

                self._detalles,

                nombre_proveedor,

            ),

        )



        self._actualizar_botones()



    def _imprimir(
        self,
    ) -> None:
        if self._factura is None:
            return
        imprimir_factura_compra(
            self._factura,
            self._detalles,
            self._nombre_proveedor,
            parent=self,
            proveedor=self._proveedor,
        )

    def _exportar_pdf(
        self,
    ) -> None:
        if self._factura is None:
            return
        exportar_pdf_factura_compra(
            self._factura,
            self._detalles,
            self._nombre_proveedor,
            parent=self,
            proveedor=self._proveedor,
        )


