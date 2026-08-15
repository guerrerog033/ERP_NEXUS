from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
)

from aplicacion.modulos.compras.facturas.datasource import (
    FacturaCompraDataSource,
)
from aplicacion.modulos.compras.facturas.formulario import (
    FormularioFacturaCompra,
)
from aplicacion.modulos.compras.facturas.vista_factura import (
    VistaFacturaCompra,
)
from aplicacion.modulos.compras.facturas.dialogo_sincronizacion_dian import (
    DialogoSincronizacionDian,
)
from aplicacion.integraciones.dian.programador_recepcion import (
    ProgramadorRecepcionCompras,
)
from aplicacion.modulos.compras.facturas.repositorio import (
    RepositorioFacturaCompra,
)


class MaestroFacturasCompra(

    CrudDocumento,

    CrudMaster,

):



    titulo = "Facturas de compra"



    titulo_singular = "Factura de compra"



    datasource = FacturaCompraDataSource



    formulario = FormularioFacturaCompra



    vista_documento = VistaFacturaCompra



    def __init__(self):



        from aplicacion.maestros.impuestos.servicios import (

            ServicioImpuesto,

        )



        ServicioImpuesto.inicializar_predeterminados()

        super().__init__()

        self._agregar_acciones_dian()
        self._configurar_sincronizacion_automatica()



    def _configurar_sincronizacion_automatica(
        self,
    ) -> None:

        self._programador = (
            ProgramadorRecepcionCompras.instancia(
                self,
            )
        )

        self._programador.sincronizacion_completada.connect(
            self._on_sincronizacion_completada,
        )

        self._actualizar_pendientes_revision()

        config = (
            ProgramadorRecepcionCompras._config()
        )

        if config.get(
            "sincronizar_al_abrir_compras",
            True,
        ) and config.get(
            "habilitado",
            False,
        ):

            QTimer.singleShot(
                500,
                self._sincronizar_automaticamente,
            )

    def _actualizar_pendientes_revision(
        self,
    ) -> None:

        if not hasattr(
            self,
            "lbl_pendientes_revision",
        ):

            return

        total = RepositorioFacturaCompra.contar_pendientes_revision()

        if total > 0:

            self.lbl_pendientes_revision.setText(
                f"{total} pendiente(s) de revisión",
            )

            self.lbl_pendientes_revision.show()

        else:

            self.lbl_pendientes_revision.hide()

    def _sincronizar_automaticamente(
        self,
    ) -> None:

        config = (
            ProgramadorRecepcionCompras._config()
        )

        if not config.get(
            "habilitado",
            False,
        ):

            return

        if not (
            config.get(
                "modo_automatico",
                False,
            )
            or config.get(
                "sincronizar_al_abrir_compras",
                True,
            )
        ):

            return

        self._programador.sincronizar_ahora(
            silencioso=True,
        )

    def _on_sincronizacion_completada(
        self,
        resultado,
    ) -> None:

        self.cargar_datos()
        self._actualizar_pendientes_revision()

        config = (
            ProgramadorRecepcionCompras._config()
        )

        if (
            not config.get(
                "notificar_nuevas",
                True,
            )
            or resultado.importadas <= 0
        ):

            return

        QMessageBox.information(
            self,
            "Facturas DIAN",
            (
                f"Se importaron {resultado.importadas} "
                f"factura(s) automáticamente.\n"
                "Revise las marcadas como "
                "pendiente de revisión."
            ),
        )

    def _agregar_acciones_dian(
        self,
    ) -> None:

        self.btn_sincronizar_dian = QPushButton(
            "Sincronizar DIAN",
        )

        self.btn_sincronizar_dian.setMinimumHeight(
            34,
        )

        self.btn_sincronizar_dian.setMinimumWidth(
            140,
        )

        self.btn_sincronizar_dian.clicked.connect(
            self._abrir_sincronizacion_dian,
        )

        self.lbl_pendientes_revision = QLabel()

        self.lbl_pendientes_revision.setStyleSheet(
            "color:#B45309;font-weight:600;padding:0 8px;",
        )

        self.lbl_pendientes_revision.hide()

        layout = self.toolbar.layout()

        if layout is not None:

            layout.insertWidget(
                layout.count() - 1,
                self.lbl_pendientes_revision,
            )

            layout.insertWidget(
                layout.count() - 1,
                self.btn_sincronizar_dian,
            )

    def _abrir_sincronizacion_dian(
        self,
    ) -> None:

        dialogo = DialogoSincronizacionDian(
            self,
        )

        if dialogo.exec():

            self.cargar_datos()



    def _titulo_dialogo_vista(

        self,

        id_registro: int,

    ) -> str:



        factura = self.datasource.obtener_completa(

            id_registro,

        )



        if factura is None:



            return "Factura de compra"



        return f"Factura {factura.numero}"



    def _tamanio_dialogo_formulario(

        self,

        formulario,

    ) -> tuple[int, int]:



        margen = self._margen_dialogo_formulario()



        ancho = min(

            formulario.ancho,

            max(

                1100,

                self.width() - margen,

            ),

        )



        alto = min(

            formulario.alto,

            max(

                520,

                self.height() - margen,

            ),

        )



        return ancho, alto



    def _titulo_dialogo_formulario(

        self,

        id_registro=None,

    ) -> str:



        if id_registro is not None:



            return "Editar factura de compra"



        return "Nueva factura de compra"


