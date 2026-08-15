from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap


class Recursos:

    # Carpeta recursos
    BASE = Path(__file__).resolve().parent.parent

    ICONO_TERCEROS = "👥"

    # ==========================
    # Iconos
    # ==========================

    @classmethod
    def icono_desde_emoji(
        cls,
        emoji: str,
        tamano: int = 32,
    ) -> QIcon:

        pixmap = QPixmap(
            tamano,
            tamano,
        )

        pixmap.fill(
            Qt.transparent,
        )

        painter = QPainter(
            pixmap,
        )

        painter.setFont(
            QFont(
                "Segoe UI Emoji",
                int(
                    tamano * 0.72,
                ),
            ),
        )

        painter.drawText(
            pixmap.rect(),
            Qt.AlignCenter,
            emoji,
        )

        painter.end()

        return QIcon(
            pixmap,
        )

    @classmethod
    def icono_terceros(
        cls,
    ) -> QIcon:

        return cls.icono_desde_emoji(
            cls.ICONO_TERCEROS,
        )

    @classmethod
    def ruta_icono(cls, nombre):

        return str(
            cls.BASE / "iconos" / f"{nombre}.svg"
        )

    @classmethod
    def ruta_icono_modulo(cls, nombre: str) -> str:

        return str(
            cls.BASE
            / "iconos"
            / "modulos"
            / f"{nombre}.svg"
        )

    @classmethod
    def icono_modulo(
        cls,
        nombre: str,
        tamano: int = 24,
    ) -> QIcon:

        ruta = Path(
            cls.ruta_icono_modulo(
                nombre,
            ),
        )

        if ruta.is_file():

            return QIcon(
                str(ruta),
            )

        return cls.icono_desde_emoji(
            "📄",
            tamano,
        )

    @classmethod
    def icono(cls, nombre):

        return QIcon(
            cls.ruta_icono(nombre)
        )

    # ==========================
    # Imágenes
    # ==========================

    @classmethod
    def ruta_imagen(cls, nombre):

        return str(
            cls.BASE / "imagenes" / nombre
        )

    @classmethod
    def imagen(cls, nombre):

        return QPixmap(
            cls.ruta_imagen(nombre)
        )

    # ==========================
    # Logos
    # ==========================

    @classmethod
    def logo_empresa(cls):

        return cls.imagen(
            "empresa/logo.png"
        )

    # ==========================
    # Productos
    # ==========================

    @classmethod
    def imagen_producto(cls, archivo):

        return cls.imagen(
            f"productos/{archivo}"
        )

    # ==========================
    # Usuarios
    # ==========================

    @classmethod
    def avatar_usuario(cls, archivo):

        return cls.imagen(
            f"usuarios/{archivo}"
        )

    # ==========================
    # Reportes
    # ==========================

    @classmethod
    def plantilla(cls, archivo):

        return str(
            cls.BASE /
            "reportes" /
            archivo
        )