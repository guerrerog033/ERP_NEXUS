"""
Barra de estado de la ventana (idea de Magister): a la izquierda la
pantalla activa con el color de su módulo y la posición del registro
("Registro 3 de 50"); a la derecha empresa, usuario, licencia y hora.
"""

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class BarraEstado(QWidget):

    def __init__(self, usuario):

        super().__init__()

        self.setObjectName("BarraEstado")
        habilitar_fondo_qss(self)
        self.setFixedHeight(26)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 12, 2)
        layout.setSpacing(0)

        nombre_erp = Configuracion.obtener("erp", "nombre") or "ERP NEXUS"
        empresa = Configuracion.obtener("empresa", "nombre") or "Empresa"

        self.lbl_modulo = QLabel("Inicio")
        self.lbl_modulo.setObjectName("BarraEstadoModulo")
        self.lbl_modulo.setAlignment(Qt.AlignCenter)
        self.lbl_modulo.setMinimumWidth(120)

        self.lbl_pantalla = QLabel("")
        self.lbl_pantalla.setObjectName("BarraEstadoTextoDestacado")

        self.lbl_registro = QLabel("")
        self.lbl_registro.setObjectName("BarraEstadoTexto")

        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setObjectName("BarraEstadoTexto")

        self.lbl_sistema = QLabel(nombre_erp)
        self.lbl_sistema.setObjectName("BarraEstadoTextoDestacado")

        self.lbl_empresa = QLabel(empresa)
        self.lbl_empresa.setObjectName("BarraEstadoTexto")

        self.lbl_usuario = QLabel(f"Usuario: {usuario.nombre}")
        self.lbl_usuario.setObjectName("BarraEstadoTexto")

        from aplicacion.nucleo.licencia import Licencia

        texto_licencia = ""

        if Licencia.habilitada():
            texto_licencia = f"Licencia: {Licencia.edicion_nombre()}"
            if Licencia.fecha_vencimiento():
                texto_licencia += (
                    " · vence "
                    f"{Licencia.fecha_vencimiento().strftime('%d/%m/%Y')}"
                )
        elif Licencia.edicion() == "desarrollo":
            texto_licencia = "Licencia: Desarrollo"

        self.lbl_licencia = QLabel(texto_licencia)
        self.lbl_licencia.setObjectName("BarraEstadoTexto")

        self.lbl_fecha = QLabel()
        self.lbl_fecha.setObjectName("BarraEstadoTexto")
        self.lbl_fecha.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.lbl_modulo)
        layout.addWidget(self._celda(self.lbl_pantalla))
        layout.addWidget(self._celda(self.lbl_registro))
        layout.addWidget(self._celda(self.lbl_mensaje), 1)

        derecha = [self.lbl_sistema, self.lbl_empresa, self.lbl_usuario]

        if texto_licencia:
            derecha.append(self.lbl_licencia)

        derecha.append(self.lbl_fecha)

        for etiqueta in derecha:
            layout.addWidget(self._celda(etiqueta))

        self.set_modulo("Inicio")
        self.set_pantalla("")
        self.set_registro("")
        self._actualizar_fecha()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._actualizar_fecha)
        self._timer.start(60000)

        self._timer_mensaje = QTimer(self)
        self._timer_mensaje.setSingleShot(True)
        self._timer_mensaje.timeout.connect(lambda: self.lbl_mensaje.setText(""))

    def _celda(self, etiqueta: QLabel) -> QFrame:
        """Cada dato en su propio recuadro hundido, como en Windows."""

        celda = QFrame()
        celda.setObjectName("BarraEstadoCelda")
        layout = QHBoxLayout(celda)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(etiqueta)
        return celda

    # -----------------------------------------------------

    def set_modulo(self, texto: str, color: str = "#1E3A5F") -> None:

        self.lbl_modulo.setText(texto or "")
        self.lbl_modulo.setStyleSheet(
            f"background: {color}; color: #FFFFFF; font-weight: 600;"
            " border-radius: 2px; padding: 1px 10px;",
        )

    def set_pantalla(self, texto: str = "") -> None:

        self.lbl_pantalla.setText(texto or "")
        self.lbl_pantalla.parentWidget().setVisible(bool(texto))

    def set_registro(self, texto: str = "") -> None:

        self.lbl_registro.setText(texto or "")
        self.lbl_registro.parentWidget().setVisible(bool(texto))

    def mensaje(self, texto: str, milisegundos: int = 5000) -> None:

        self.lbl_mensaje.setText(texto or "")

        if milisegundos:
            self._timer_mensaje.start(milisegundos)

    def _actualizar_fecha(self) -> None:

        self.lbl_fecha.setText(datetime.now().strftime("%d/%m/%Y  %H:%M"))
