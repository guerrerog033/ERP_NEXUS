from __future__ import annotations

from pathlib import Path

from aplicacion.nucleo.configuracion import Configuracion


class FirmadorXml:

    @classmethod
    def _ruta_certificado(cls) -> Path | None:

        ruta = Configuracion.obtener(
            "dian",
            "certificado_ruta",
        )

        if not ruta:

            return None

        archivo = Path(str(ruta))

        if not archivo.is_file():

            return None

        return archivo

    @classmethod
    def _clave_certificado(cls) -> str:

        return str(
            Configuracion.obtener(
                "dian",
                "certificado_clave",
            )
            or "",
        )

    @classmethod
    def firmar(
        cls,
        xml: str,
        *,
        ruta_salida: str | None = None,
    ) -> str:

        certificado = cls._ruta_certificado()

        if certificado is None:

            raise ValueError(
                "Configure dian.certificado_ruta "
                "con el archivo .p12/.pfx.",
            )

        clave = cls._clave_certificado()

        if not clave:

            raise ValueError(
                "Configure dian.certificado_clave "
                "con la contraseña del certificado.",
            )

        try:

            from cryptography.hazmat.primitives.serialization import (
                pkcs12,
            )
            from lxml import etree
            from signxml import (
                XMLSigner,
                methods,
            )

        except ImportError as error:

            raise ValueError(
                "Instale las dependencias de firma: "
                "pip install lxml signxml cryptography"
            ) from error

        contenido = certificado.read_bytes()

        clave_bytes = clave.encode("utf-8")

        private_key, certificate, _ = (
            pkcs12.load_key_and_certificates(
                contenido,
                clave_bytes,
            )
        )

        if private_key is None or certificate is None:

            raise ValueError(
                "No se pudo leer el certificado digital.",
            )

        documento = etree.fromstring(
            xml.encode("utf-8"),
        )

        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha256",
            digest_algorithm="sha256",
            c14n_algorithm=(
                "http://www.w3.org/TR/2001/"
                "REC-xml-c14n-20010315"
            ),
        )

        signed = signer.sign(
            documento,
            key=private_key,
            cert=[certificate],
            reference_uri="",
        )

        xml_firmado = etree.tostring(
            signed,
            encoding="utf-8",
            xml_declaration=True,
        ).decode("utf-8")

        if ruta_salida:

            Path(ruta_salida).write_text(
                xml_firmado,
                encoding="utf-8",
            )

        return xml_firmado
