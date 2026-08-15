from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from aplicacion.nucleo.configuracion import Configuracion


@dataclass(slots=True)
class DatosEmisionNominaElectronica:

    xml: str
    cune: str
    ruta_xml: str
    numero: str


class GeneradorNominaElectronica:

    @classmethod
    def _ambiente(cls) -> str:

        ambiente = str(
            Configuracion.obtener(
                "dian",
                "ambiente_emision",
            )
            or Configuracion.obtener(
                "dian",
                "ambiente",
            )
            or "habilitacion",
        ).lower()

        if ambiente in (
            "habilitacion",
            "pruebas",
            "test",
        ):

            return "2"

        return "1"

    @classmethod
    def _empresa(cls) -> tuple[str, str, str]:

        nit = str(
            Configuracion.obtener(
                "empresa",
                "nit",
            )
            or "",
        ).strip()

        razon = str(
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or "Empresa",
        ).strip()

        dv = str(
            Configuracion.obtener(
                "empresa",
                "dv",
            )
            or "",
        ).strip()

        return nit, razon, dv

    @classmethod
    def _directorio_salida(cls) -> Path:

        ruta = Path(
            Configuracion.obtener(
                "nomina",
                "ruta_xml_dian",
            )
            or "salida/nomina/dian",
        )

        ruta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return ruta

    @classmethod
    def _calcular_cune(
        cls,
        *,
        numero: str,
        fecha: str,
        hora: datetime,
        valor: float,
        nit: str,
        software_pin: str,
    ) -> str:

        cadena = (
            f"{numero}^{fecha}^{hora.strftime('%H:%M:%S-05:00')}^"
            f"{valor:.2f}^{nit}^{software_pin}^"
            f"{cls._ambiente()}"
        )

        return hashlib.sha384(
            cadena.encode("utf-8"),
        ).hexdigest()

    @classmethod
    def generar(
        cls,
        *,
        numero: str,
        anio: int,
        mes: int,
        valor_total: float,
        trabajadores: list[dict],
    ) -> DatosEmisionNominaElectronica:
        """
        Genera XML de nómina electrónica DIAN (estructura operativa UBL).
        """

        nit, razon, dv = cls._empresa()
        ahora = datetime.now()
        fecha = f"{anio:04d}-{mes:02d}-01"
        software_pin = str(
            Configuracion.obtener(
                "dian",
                "software_pin",
            )
            or "12345",
        )

        cune = cls._calcular_cune(
            numero=numero,
            fecha=fecha,
            hora=ahora,
            valor=valor_total,
            nit=nit,
            software_pin=software_pin,
        )

        lineas_trabajadores = []

        for trabajador in trabajadores:

            lineas_trabajadores.append(
                "    <Trabajador>"
                f"<TipoDocumento>{escape(str(trabajador.get('tipo_documento', 'CC')))}</TipoDocumento>"
                f"<NumeroDocumento>{escape(str(trabajador.get('numero_documento', '')))}</NumeroDocumento>"
                f"<Nombre>{escape(str(trabajador.get('empleado', '')))}</Nombre>"
                f"<Devengado>{float(trabajador.get('devengado', 0) or 0):.2f}</Devengado>"
                f"<Deducciones>{float(trabajador.get('salud_empleado', 0) or 0) + float(trabajador.get('pension_empleado', 0) or 0):.2f}</Deducciones>"
                f"<Neto>{float(trabajador.get('neto', 0) or 0):.2f}</Neto>"
                "</Trabajador>"
            )

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<NominaIndividual xmlns="dian:gov:co:facturaelectronica:NominaIndividual"
                  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
  <cbc:ProfileID>DIAN 2.1: NominaIndividual</cbc:ProfileID>
  <cbc:ID>{escape(numero)}</cbc:ID>
  <cbc:IssueDate>{fecha}</cbc:IssueDate>
  <cbc:IssueTime>{ahora.strftime('%H:%M:%S-05:00')}</cbc:IssueTime>
  <Ambiente>{cls._ambiente()}</Ambiente>
  <Empleador>
    <NIT>{escape(nit)}</NIT>
    <DV>{escape(dv)}</DV>
    <RazonSocial>{escape(razon)}</RazonSocial>
  </Empleador>
  <PeriodoNomina>{anio:04d}-{mes:02d}</PeriodoNomina>
  <NumeroTrabajadores>{len(trabajadores)}</NumeroTrabajadores>
  <ValorTotalNomina>{valor_total:.2f}</ValorTotalNomina>
  <Trabajadores>
{chr(10).join(lineas_trabajadores)}
  </Trabajadores>
  <CUNE>{cune}</CUNE>
</NominaIndividual>"""

        nombre = f"NE_{anio:04d}{mes:02d}_{numero}.xml"
        ruta = cls._directorio_salida() / nombre

        ruta.write_text(
            xml,
            encoding="utf-8",
        )

        return DatosEmisionNominaElectronica(
            xml=xml,
            cune=cune,
            ruta_xml=str(ruta),
            numero=numero,
        )
