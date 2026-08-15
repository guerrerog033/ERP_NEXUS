from datetime import datetime



from PySide6.QtCore import QTimer, Qt

from PySide6.QtWidgets import (

    QWidget,

    QLabel,

    QHBoxLayout,

)



from aplicacion.nucleo.configuracion import Configuracion

from aplicacion.recursos.estilos.tema import habilitar_fondo_qss





class BarraEstado(QWidget):



    def __init__(

        self,

        usuario,

    ):



        super().__init__()



        self.setObjectName(

            "BarraEstado",

        )



        habilitar_fondo_qss(

            self,

        )



        self.setFixedHeight(

            28,

        )



        layout = QHBoxLayout(

            self,

        )



        layout.setContentsMargins(

            16,

            0,

            16,

            0,

        )



        layout.setSpacing(

            20,

        )



        nombre_erp = (

            Configuracion.obtener(

                "erp",

                "nombre",

            )

            or "ERP NEXUS"

        )



        empresa = (

            Configuracion.obtener(

                "empresa",

                "nombre",

            )

            or "Empresa"

        )



        self.lbl_sistema = QLabel(

            nombre_erp,

        )



        self.lbl_sistema.setObjectName(

            "BarraEstadoTextoDestacado",

        )



        self.lbl_empresa = QLabel(

            empresa,

        )



        self.lbl_empresa.setObjectName(

            "BarraEstadoTexto",

        )



        self.lbl_usuario = QLabel(

            f"Usuario: {usuario.nombre}",

        )

        from aplicacion.nucleo.licencia import Licencia

        texto_licencia = ""

        if Licencia.habilitada():

            texto_licencia = (
                f"Licencia: {Licencia.edicion_nombre()}"
            )

            if Licencia.fecha_vencimiento():

                texto_licencia += (
                    " · vence "
                    f"{Licencia.fecha_vencimiento().strftime('%d/%m/%Y')}"
                )

        elif Licencia.edicion() == "desarrollo":

            texto_licencia = "Licencia: Desarrollo"

        self.lbl_licencia = QLabel(
            texto_licencia,
        )

        self.lbl_licencia.setObjectName(
            "BarraEstadoTexto",
        )



        self.lbl_usuario.setObjectName(

            "BarraEstadoTexto",

        )



        self.lbl_fecha = QLabel()



        self.lbl_fecha.setObjectName(

            "BarraEstadoTexto",

        )



        self.lbl_fecha.setAlignment(

            Qt.AlignRight

            | Qt.AlignVCenter,

        )



        layout.addWidget(

            self.lbl_sistema,

        )



        layout.addWidget(

            self.lbl_empresa,

        )



        layout.addStretch()



        layout.addWidget(

            self.lbl_usuario,

        )

        if texto_licencia:

            layout.addWidget(

                self.lbl_licencia,

            )



        layout.addWidget(

            self.lbl_fecha,

        )



        self._actualizar_fecha()



        self._timer = QTimer(

            self,

        )



        self._timer.timeout.connect(

            self._actualizar_fecha,

        )



        self._timer.start(

            60000,

        )



    def _actualizar_fecha(

        self,

    ) -> None:



        self.lbl_fecha.setText(

            datetime.now().strftime(

                "%d/%m/%Y  %H:%M",

            ),

        )

