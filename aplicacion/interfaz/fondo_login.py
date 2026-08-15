from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QPointF
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


def _dibujar_rejilla(
    painter: QPainter,
    rect: QRect,
) -> None:

    ancho = rect.width()
    alto = rect.height()

    painter.setPen(
        QPen(
            QColor(
                255,
                255,
                255,
                16,
            ),
            1,
        ),
    )

    paso = 48

    for x in range(
        0,
        ancho,
        paso,
    ):

        painter.drawLine(
            x,
            0,
            x,
            alto,
        )

    for y in range(
        0,
        alto,
        paso,
    ):

        painter.drawLine(
            0,
            y,
            ancho,
            y,
        )


def _dibujar_puntos(
    painter: QPainter,
    rect: QRect,
) -> None:

    ancho = rect.width()
    alto = rect.height()

    painter.setPen(
        Qt.PenStyle.NoPen,
    )

    for x in range(
        24,
        ancho - 24,
        28,
    ):

        for y in range(
            24,
            alto - 24,
            28,
        ):

            distancia = abs(
                x - ancho * 0.35,
            ) / max(
                ancho,
                1,
            )

            alpha = max(
                8,
                int(
                    28
                    - distancia * 40,
                ),
            )

            painter.setBrush(
                QColor(
                    255,
                    255,
                    255,
                    alpha,
                ),
            )

            painter.drawEllipse(
                x,
                y,
                3,
                3,
            )


def _dibujar_logo_nexus(
    painter: QPainter,
    cx: float,
    cy: float,
    radio: float,
) -> None:

    anillo = QRadialGradient(
        cx,
        cy,
        radio * 1.4,
    )

    anillo.setColorAt(
        0.0,
        QColor(
            255,
            255,
            255,
            45,
        ),
    )

    anillo.setColorAt(
        1.0,
        QColor(
            255,
            255,
            255,
            0,
        ),
    )

    painter.setPen(
        Qt.PenStyle.NoPen,
    )

    painter.setBrush(
        anillo,
    )

    painter.drawEllipse(
        int(
            cx - radio * 1.4,
        ),
        int(
            cy - radio * 1.4,
        ),
        int(
            radio * 2.8,
        ),
        int(
            radio * 2.8,
        ),
    )

    gradiente = QLinearGradient(
        cx - radio,
        cy - radio,
        cx + radio,
        cy + radio,
    )

    gradiente.setColorAt(
        0.0,
        QColor(
            "#3A7BC5",
        ),
    )

    gradiente.setColorAt(
        1.0,
        QColor(
            "#1B4F8A",
        ),
    )

    painter.setBrush(
        gradiente,
    )

    painter.setPen(
        QPen(
            QColor(
                255,
                255,
                255,
                90,
            ),
            2,
        ),
    )

    painter.drawEllipse(
        int(
            cx - radio,
        ),
        int(
            cy - radio,
        ),
        int(
            radio * 2,
        ),
        int(
            radio * 2,
        ),
    )

    fuente = QFont(
        "Segoe UI",
        int(
            radio * 0.95,
        ),
        QFont.Weight.Bold,
    )

    painter.setFont(
        fuente,
    )

    painter.setPen(
        QColor(
            "#FFFFFF",
        ),
    )

    painter.drawText(
        QRect(
            int(
                cx - radio,
            ),
            int(
                cy - radio,
            ),
            int(
                radio * 2,
            ),
            int(
                radio * 2,
            ),
        ),
        int(
            Qt.AlignmentFlag.AlignCenter,
        ),
        "N",
    )


def _dibujar_tarjeta_modulo(
    painter: QPainter,
    x: float,
    y: float,
    ancho: float,
    alto: float,
    titulo: str,
    icono: str,
    alpha_fondo: int,
) -> None:

    path = QPainterPath()

    path.addRoundedRect(
        x,
        y,
        ancho,
        alto,
        10,
        10,
    )

    painter.setPen(
        QPen(
            QColor(
                255,
                255,
                255,
                55,
            ),
            1,
        ),
    )

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            alpha_fondo,
        ),
    )

    painter.drawPath(
        path,
    )

    fuente_icono = QFont(
        "Segoe UI Emoji",
        16,
    )

    painter.setFont(
        fuente_icono,
    )

    painter.setPen(
        QColor(
            255,
            255,
            255,
            210,
        ),
    )

    painter.drawText(
        QRect(
            int(
                x + 12,
            ),
            int(
                y + 8,
            ),
            28,
            28,
        ),
        int(
            Qt.AlignmentFlag.AlignCenter,
        ),
        icono,
    )

    fuente = QFont(
        "Segoe UI",
        9,
        QFont.Weight.DemiBold,
    )

    painter.setFont(
        fuente,
    )

    painter.drawText(
        QRect(
            int(
                x + 42,
            ),
            int(
                y + 10,
            ),
            int(
                ancho - 50,
            ),
            int(
                alto - 16,
            ),
        ),
        int(
            Qt.AlignmentFlag.AlignVCenter,
        ),
        titulo,
    )


def _dibujar_modulos_flotantes(
    painter: QPainter,
    ancho: float,
    alto: float,
) -> None:

    modulos = (
        (0.58, 0.14, "Ventas", "📈"),
        (0.72, 0.22, "Compras", "🛒"),
        (0.64, 0.38, "Inventario", "📦"),
        (0.78, 0.48, "Finanzas", "💰"),
        (0.55, 0.52, "Contabilidad", "📊"),
        (0.70, 0.62, "DIAN / FE", "🧾"),
    )

    for indice, (
        fx,
        fy,
        titulo,
        icono,
    ) in enumerate(
        modulos,
    ):

        _dibujar_tarjeta_modulo(
            painter,
            ancho * fx,
            alto * fy,
            132,
            44,
            titulo,
            icono,
            18
            + indice * 3,
        )


def _dibujar_panel_dashboard(
    painter: QPainter,
    x: float,
    y: float,
    ancho: float,
    alto: float,
) -> None:

    painter.setPen(
        QPen(
            QColor(
                255,
                255,
                255,
                40,
            ),
            1,
        ),
    )

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            12,
        ),
    )

    painter.drawRoundedRect(
        int(
            x,
        ),
        int(
            y,
        ),
        int(
            ancho,
        ),
        int(
            alto,
        ),
        14,
        14,
    )

    painter.setPen(
        QPen(
            QColor(
                255,
                255,
                255,
                70,
            ),
            2,
        ),
    )

    base_y = y + alto - 28

    barras = (
        0.18,
        0.32,
        0.24,
        0.42,
        0.30,
    )

    for indice, factor in enumerate(
        barras,
    ):

        bx = x + 18 + indice * 28

        bh = factor * (alto - 56)

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                35,
            ),
        )

        painter.drawRoundedRect(
            int(
                bx,
            ),
            int(
                base_y - bh,
            ),
            18,
            int(
                bh,
            ),
            3,
            3,
        )

    centro_x = x + ancho - 58
    centro_y = y + 42

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            28,
        ),
    )

    painter.drawPie(
        int(
            centro_x - 22,
        ),
        int(
            centro_y - 22,
        ),
        44,
        44,
        30 * 16,
        120 * 16,
    )

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            18,
        ),
    )

    painter.drawPie(
        int(
            centro_x - 22,
        ),
        int(
            centro_y - 22,
        ),
        44,
        44,
        150 * 16,
        140 * 16,
    )

    fuente = QFont(
        "Segoe UI",
        8,
        QFont.Weight.Bold,
    )

    painter.setFont(
        fuente,
    )

    painter.setPen(
        QColor(
            255,
            255,
            255,
            120,
        ),
    )

    painter.drawText(
        QRect(
            int(
                x + 12,
            ),
            int(
                y + 10,
            ),
            int(
                ancho - 24,
            ),
            20,
        ),
        int(
            Qt.AlignmentFlag.AlignLeft,
        ),
        "Panel ERP",
    )


def _dibujar_documentos(
    painter: QPainter,
    x: float,
    y: float,
) -> None:

    for indice in range(
        3,
    ):

        desplazamiento = indice * 6

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                    50 - indice * 10,
                ),
                1,
            ),
        )

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                16 - indice * 4,
            ),
        )

        painter.drawRoundedRect(
            int(
                x + desplazamiento,
            ),
            int(
                y + desplazamiento,
            ),
            54,
            68,
            4,
            4,
        )

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                    70,
                ),
                1,
            ),
        )

        for linea in range(
            3,
        ):

            ly = y + desplazamiento + 14 + linea * 10

            painter.drawLine(
                int(
                    x + desplazamiento + 8,
                ),
                int(
                    ly,
                ),
                int(
                    x + desplazamiento + 42,
                ),
                int(
                    ly,
                ),
            )


def _dibujar_red_datos(
    painter: QPainter,
    ancho: float,
    alto: float,
) -> None:

    nodos = [
        (ancho * 0.46, alto * 0.72),
        (ancho * 0.52, alto * 0.78),
        (ancho * 0.58, alto * 0.74),
        (ancho * 0.54, alto * 0.66),
        (ancho * 0.48, alto * 0.64),
    ]

    painter.setPen(
        QPen(
            QColor(
                255,
                255,
                255,
                45,
            ),
            1,
        ),
    )

    for indice in range(
        len(
            nodos,
        )
        - 1,
    ):

        x1, y1 = nodos[
            indice
        ]

        x2, y2 = nodos[
            indice
            + 1
        ]

        painter.drawLine(
            int(
                x1,
            ),
            int(
                y1,
            ),
            int(
                x2,
            ),
            int(
                y2,
            ),
        )

    painter.setPen(
        Qt.PenStyle.NoPen,
    )

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            55,
        ),
    )

    for x, y in nodos:

        painter.drawEllipse(
            QPointF(
                x,
                y,
            ),
            4,
            4,
        )


def _dibujar_barras_crecimiento(
    painter: QPainter,
    ancho: float,
    alto: float,
) -> None:

    base_barras = int(
        alto * 0.78,
    )

    inicio_barras = int(
        ancho * 0.05,
    )

    alturas = (
        70,
        110,
        88,
        132,
        98,
        118,
    )

    painter.setPen(
        Qt.PenStyle.NoPen,
    )

    puntos = []

    for indice, altura in enumerate(
        alturas,
    ):

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                28
                + indice * 6,
            ),
        )

        x = inicio_barras + indice * 34

        painter.drawRoundedRect(
            x,
            base_barras - altura,
            22,
            altura,
            4,
            4,
        )

        puntos.append(
            (
                x + 11,
                base_barras - altura,
            ),
        )

    if len(
        puntos,
    ) >= 2:

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                    130,
                ),
                2,
            ),
        )

        for indice in range(
            len(
                puntos,
            )
            - 1,
        ):

            x1, y1 = puntos[
                indice
            ]

            x2, y2 = puntos[
                indice
                + 1
            ]

            painter.drawLine(
                x1,
                y1,
                x2,
                y2,
            )


def _dibujar_ondas(
    painter: QPainter,
    ancho: float,
    alto: float,
) -> None:

    onda = QPainterPath()

    onda.moveTo(
        0,
        alto,
    )

    onda.lineTo(
        0,
        alto * 0.9,
    )

    onda.quadTo(
        ancho * 0.22,
        alto * 0.82,
        ancho * 0.45,
        alto * 0.9,
    )

    onda.quadTo(
        ancho * 0.68,
        alto * 0.98,
        ancho,
        alto * 0.86,
    )

    onda.lineTo(
        ancho,
        alto,
    )

    onda.closeSubpath()

    painter.setPen(
        Qt.PenStyle.NoPen,
    )

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            16,
        ),
    )

    painter.drawPath(
        onda,
    )

    onda2 = QPainterPath()

    onda2.moveTo(
        0,
        alto,
    )

    onda2.lineTo(
        0,
        alto * 0.94,
    )

    onda2.quadTo(
        ancho * 0.35,
        alto * 0.88,
        ancho * 0.62,
        alto * 0.95,
    )

    onda2.quadTo(
        ancho * 0.85,
        alto * 1.0,
        ancho,
        alto * 0.92,
    )

    onda2.lineTo(
        ancho,
        alto,
    )

    onda2.closeSubpath()

    painter.setBrush(
        QColor(
            255,
            255,
            255,
            10,
        ),
    )

    painter.drawPath(
        onda2,
    )


def pintar_fondo_login(
    painter: QPainter,
    rect: QRect,
) -> None:

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
    )

    ancho = rect.width()
    alto = rect.height()

    gradiente = QLinearGradient(
        0,
        0,
        ancho,
        alto,
    )

    gradiente.setColorAt(
        0.0,
        QColor(
            "#051628",
        ),
    )

    gradiente.setColorAt(
        0.18,
        QColor(
            "#0A2848",
        ),
    )

    gradiente.setColorAt(
        0.42,
        QColor(
            "#123D6E",
        ),
    )

    gradiente.setColorAt(
        0.68,
        QColor(
            "#2E6BA8",
        ),
    )

    gradiente.setColorAt(
        1.0,
        QColor(
            "#8EC5EA",
        ),
    )

    painter.fillRect(
        rect,
        gradiente,
    )

    brillo = QRadialGradient(
        ancho * 0.78,
        alto * 0.22,
        max(
            ancho,
            alto,
        )
        * 0.55,
    )

    brillo.setColorAt(
        0.0,
        QColor(
            255,
            255,
            255,
            55,
        ),
    )

    brillo.setColorAt(
        1.0,
        QColor(
            255,
            255,
            255,
            0,
        ),
    )

    painter.fillRect(
        rect,
        brillo,
    )

    brillo_izq = QRadialGradient(
        ancho * 0.12,
        alto * 0.55,
        alto * 0.45,
    )

    brillo_izq.setColorAt(
        0.0,
        QColor(
            58,
            123,
            197,
            40,
        ),
    )

    brillo_izq.setColorAt(
        1.0,
        QColor(
            58,
            123,
            197,
            0,
        ),
    )

    painter.fillRect(
        rect,
        brillo_izq,
    )

    _dibujar_rejilla(
        painter,
        rect,
    )

    _dibujar_puntos(
        painter,
        rect,
    )

    _dibujar_logo_nexus(
        painter,
        ancho * 0.11,
        alto * 0.24,
        36,
    )

    _dibujar_barras_crecimiento(
        painter,
        ancho,
        alto,
    )

    _dibujar_panel_dashboard(
        painter,
        ancho * 0.68,
        alto * 0.68,
        190,
        120,
    )

    _dibujar_documentos(
        painter,
        ancho * 0.82,
        alto * 0.12,
    )

    _dibujar_modulos_flotantes(
        painter,
        ancho,
        alto,
    )

    _dibujar_red_datos(
        painter,
        ancho,
        alto,
    )

    _dibujar_ondas(
        painter,
        ancho,
        alto,
    )


class FondoLogin(QWidget):
    """Fondo decorativo del inicio de sesión."""

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setAttribute(
            Qt.WA_StyledBackground,
            False,
        )

        self.setAutoFillBackground(
            False,
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(
            self,
        )

        pintar_fondo_login(
            painter,
            self.rect(),
        )

        painter.end()
