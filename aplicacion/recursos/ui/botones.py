from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from aplicacion.recursos.ui.recursos import Recursos


class Botones:

    @staticmethod
    def _crear(
        texto: str,
        object_name: str,
        icono: str | None = None,
    ) -> QPushButton:

        boton = QPushButton(
            texto,
        )

        boton.setObjectName(
            object_name,
        )

        if icono is not None:

            boton.setIcon(
                Recursos.icono(
                    icono,
                ),
            )

            boton.setIconSize(
                QSize(
                    20,
                    20,
                ),
            )

        return boton

    @staticmethod
    def primario(
        texto: str = "Aceptar",
    ) -> QPushButton:

        return Botones._crear(
            texto,
            "BotonPrimario",
            "acciones/aceptar",
        )

    @staticmethod
    def secundario(
        texto: str = "Cancelar",
    ) -> QPushButton:

        return Botones._crear(
            texto,
            "BotonSecundario",
            "acciones/cancelar",
        )

    @staticmethod
    def peligro(
        texto: str = "Eliminar",
    ) -> QPushButton:

        return Botones._crear(
            texto,
            "BotonPeligro",
            "acciones/eliminar",
        )

    @staticmethod
    def guardar():

        return Botones._crear(
            "Guardar",
            "BotonPrimario",
            "acciones/guardar",
        )

    @staticmethod
    def nuevo():

        return Botones._crear(
            "Nuevo",
            "BotonPrimario",
            "acciones/nuevo",
        )

    @staticmethod
    def editar():

        return Botones._crear(
            "Editar",
            "BotonSecundario",
            "acciones/editar",
        )

    @staticmethod
    def eliminar():

        return Botones.peligro()

    @staticmethod
    def actualizar():

        return Botones._crear(
            "Actualizar",
            "BotonSecundario",
            "acciones/actualizar",
        )

    @staticmethod
    def cancelar():

        return Botones.secundario()

    @staticmethod
    def cerrar():

        return Botones._crear(
            "Cerrar",
            "BotonSecundario",
            "acciones/cerrar",
        )

    @staticmethod
    def aceptar():

        return Botones.primario()

    @staticmethod
    def buscar():

        return Botones._crear(
            "Buscar",
            "BotonSecundario",
            "acciones/buscar",
        )
