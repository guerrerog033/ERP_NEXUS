from __future__ import annotations

import base64
import io


def generar_qr_data_uri(
    texto: str,
    *,
    tamano: int = 4,
) -> str:
    """Genera QR como data URI PNG (requiere qrcode)."""

    try:
        import qrcode

        imagen = qrcode.make(
            str(texto or ""),
            box_size=tamano,
            border=2,
        )

        buffer = io.BytesIO()
        imagen.save(
            buffer,
            format="PNG",
        )

        datos = base64.b64encode(
            buffer.getvalue(),
        ).decode("ascii")

        return f"data:image/png;base64,{datos}"

    except ImportError:
        return (
            "data:image/svg+xml;base64,"
            + base64.b64encode(
                (
                    f'<svg xmlns="http://www.w3.org/2000/svg" '
                    f'width="160" height="160">'
                    f'<rect width="100%" height="100%" fill="#eee"/>'
                    f'<text x="10" y="80" font-size="10">QR</text>'
                    f"</svg>"
                ).encode("utf-8"),
            ).decode("ascii")
        )
