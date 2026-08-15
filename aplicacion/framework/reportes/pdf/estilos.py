from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


AZUL_NEXUS = colors.HexColor("#1557A6")
AZUL_OSCURO = colors.HexColor("#12355B")
AZUL_CLARO = colors.HexColor("#EAF2FB")

GRIS = colors.HexColor("#6B7280")
GRIS_CLARO = colors.HexColor("#F3F4F6")
GRIS_BORDE = colors.HexColor("#D9DEE7")

VERDE = colors.HexColor("#16A34A")
ROJO = colors.HexColor("#DC2626")

BLANCO = colors.white
NEGRO = colors.HexColor("#111827")


def estilos_reportlab() -> dict[str, ParagraphStyle]:

    base = getSampleStyleSheet()

    return {
        "titulo": ParagraphStyle(
            "titulo",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            textColor=AZUL_OSCURO,
            alignment=TA_LEFT,
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=AZUL_NEXUS,
        ),
        "normal": ParagraphStyle(
            "normal",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=NEGRO,
        ),
        "pequeno": ParagraphStyle(
            "pequeno",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=GRIS,
        ),
        "derecha": ParagraphStyle(
            "derecha",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=NEGRO,
            alignment=TA_RIGHT,
        ),
        "derecha_bold": ParagraphStyle(
            "derecha_bold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=NEGRO,
            alignment=TA_RIGHT,
        ),
        "centro": ParagraphStyle(
            "centro",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=NEGRO,
            alignment=TA_CENTER,
        ),
    }
