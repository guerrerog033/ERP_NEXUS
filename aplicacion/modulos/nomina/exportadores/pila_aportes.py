from __future__ import annotations

from pathlib import Path

from aplicacion.nucleo.configuracion import Configuracion

from ..constantes import (
    CODIGO_ARL_DEFECTO,
)
from .pila_formato import (
    REGISTRO_01_LONGITUD,
    REGISTRO_02_LONGITUD,
    RegistroPilaBuilder,
    tarifa_pila,
)


class ExportadorPilaAportesEnLinea:

    @classmethod
    def _directorio_salida(cls) -> Path:

        ruta = Path(
            Configuracion.obtener(
                "nomina",
                "ruta_pila",
            )
            or "salida/nomina/pila",
        )

        ruta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return ruta

    @classmethod
    def _registro_tipo1_aportante(
        cls,
        *,
        razon_social: str,
        nit: str,
        dv: str,
    ) -> str:

        registro = RegistroPilaBuilder(
            REGISTRO_01_LONGITUD,
        )

        registro.escribir(
            1,
            200,
            razon_social,
        )
        registro.escribir(
            201,
            2,
            "NI",
        )
        registro.escribir(
            203,
            16,
            nit,
        )
        registro.escribir(
            219,
            1,
            dv or "0",
            numerico=True,
        )
        registro.escribir(
            270,
            1,
            "B",
        )
        registro.escribir(
            272,
            1,
            "U",
        )

        return registro.render()

    @classmethod
    def _registro_encabezado_planilla(
        cls,
        *,
        razon_social: str,
        nit: str,
        dv: str,
        anio: int,
        mes: int,
        arl_codigo: str,
    ) -> str:

        periodo = f"{anio:04d}-{mes:02d}"

        registro = RegistroPilaBuilder(
            REGISTRO_01_LONGITUD,
        )

        registro.escribir(
            1,
            2,
            "01",
            numerico=True,
        )
        registro.escribir(
            3,
            1,
            "1",
            numerico=True,
        )
        registro.escribir(
            4,
            4,
            "0001",
            numerico=True,
        )
        registro.escribir(
            8,
            200,
            razon_social,
        )
        registro.escribir(
            208,
            2,
            "NI",
        )
        registro.escribir(
            210,
            16,
            nit,
        )
        registro.escribir(
            226,
            1,
            dv or "0",
            numerico=True,
        )
        registro.escribir(
            227,
            1,
            "E",
        )
        registro.escribir(
            248,
            1,
            "U",
        )
        registro.escribir(
            299,
            6,
            arl_codigo or CODIGO_ARL_DEFECTO,
        )
        registro.escribir(
            305,
            7,
            periodo,
        )
        registro.escribir(
            312,
            7,
            periodo,
        )

        return registro.render()

    @classmethod
    def _registro_detalle_cotizante(
        cls,
        *,
        secuencia: int,
        fila: dict,
    ) -> str:

        registro = RegistroPilaBuilder(
            REGISTRO_02_LONGITUD,
        )

        registro.escribir(
            1,
            2,
            "02",
            numerico=True,
        )
        registro.escribir(
            3,
            5,
            secuencia,
            numerico=True,
        )
        registro.escribir(
            8,
            2,
            fila.get(
                "tipo_documento",
                "CC",
            ),
        )
        registro.escribir(
            10,
            16,
            fila.get(
                "numero_documento",
                "",
            ),
        )
        registro.escribir(
            26,
            2,
            fila.get(
                "tipo_cotizante",
                "01",
            ),
            numerico=True,
        )
        registro.escribir(
            28,
            2,
            fila.get(
                "subtipo_cotizante",
                "00",
            ),
            numerico=True,
        )
        registro.escribir(
            32,
            2,
            fila.get(
                "departamento",
                "11",
            ),
        )
        registro.escribir(
            34,
            3,
            fila.get(
                "municipio",
                "001",
            ),
        )
        registro.escribir(
            37,
            20,
            fila.get(
                "primer_apellido",
                "",
            ),
        )
        registro.escribir(
            57,
            30,
            fila.get(
                "segundo_apellido",
                "",
            ),
        )
        registro.escribir(
            87,
            20,
            fila.get(
                "primer_nombre",
                "",
            ),
        )
        registro.escribir(
            107,
            30,
            fila.get(
                "segundo_nombre",
                "",
            ),
        )

        if fila.get(
            "novedad_ige",
        ):

            registro.escribir(
                147,
                1,
                "X",
            )

        registro.escribir(
            166,
            6,
            fila.get(
                "afp_codigo",
                "",
            ),
        )
        registro.escribir(
            172,
            6,
            fila.get(
                "eps_codigo",
                "",
            ),
        )
        registro.escribir(
            178,
            6,
            fila.get(
                "ccf_codigo",
                "",
            ),
        )

        dias = int(
            fila.get(
                "dias_cotizados",
                30,
            )
            or 30,
        )

        registro.escribir(
            184,
            2,
            dias,
            numerico=True,
        )
        registro.escribir(
            186,
            2,
            dias,
            numerico=True,
        )
        registro.escribir(
            188,
            2,
            dias,
            numerico=True,
        )
        registro.escribir(
            190,
            2,
            dias,
            numerico=True,
        )

        salario = int(
            float(
                fila.get(
                    "salario_basico",
                    0,
                )
                or 0,
            ),
        )

        ibc = int(
            float(
                fila.get(
                    "ibc",
                    0,
                )
                or 0,
            ),
        )

        registro.escribir(
            192,
            9,
            salario,
            numerico=True,
        )

        if fila.get(
            "salario_integral",
        ):

            registro.escribir(
                201,
                1,
                "X",
            )

        registro.escribir(
            202,
            9,
            ibc,
            numerico=True,
        )
        registro.escribir(
            211,
            9,
            ibc,
            numerico=True,
        )
        registro.escribir(
            220,
            9,
            ibc,
            numerico=True,
        )
        registro.escribir(
            229,
            9,
            ibc,
            numerico=True,
        )

        registro.escribir(
            238,
            7,
            tarifa_pila(0.12),
        )
        registro.escribir(
            245,
            9,
            int(
                fila.get(
                    "pension_patronal",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )
        registro.escribir(
            281,
            9,
            int(
                fila.get(
                    "fsp",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )
        registro.escribir(
            308,
            7,
            tarifa_pila(0.085),
        )
        registro.escribir(
            315,
            9,
            int(
                fila.get(
                    "salud_patronal",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )

        tarifa_arl = float(
            fila.get(
                "tarifa_arl",
                0.00522,
            )
            or 0.00522,
        )

        registro.escribir(
            381,
            9,
            tarifa_pila(
                tarifa_arl,
            ),
        )
        registro.escribir(
            390,
            9,
            int(
                fila.get(
                    "centro_trabajo",
                    1,
                )
                or 1,
            ),
            numerico=True,
        )
        registro.escribir(
            399,
            9,
            int(
                fila.get(
                    "arl_valor",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )
        registro.escribir(
            408,
            7,
            tarifa_pila(0.04),
        )
        registro.escribir(
            415,
            9,
            int(
                fila.get(
                    "caja",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )
        registro.escribir(
            424,
            7,
            tarifa_pila(0.02),
        )
        registro.escribir(
            431,
            9,
            int(
                fila.get(
                    "sena",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )
        registro.escribir(
            440,
            7,
            tarifa_pila(0.03),
        )
        registro.escribir(
            447,
            9,
            int(
                fila.get(
                    "icbf",
                    0,
                )
                or 0,
            ),
            numerico=True,
        )
        registro.escribir(
            507,
            6,
            fila.get(
                "arl_codigo",
                CODIGO_ARL_DEFECTO,
            ),
        )
        registro.escribir(
            513,
            1,
            fila.get(
                "clase_riesgo",
                "1",
            ),
        )

        return registro.render()

    @classmethod
    def generar(
        cls,
        *,
        anio: int,
        mes: int,
        aportante: dict,
        liquidaciones: list[dict],
    ) -> dict[str, str]:
        """
        Genera archivos planos PILA (Res. 2388) para Aportes en Línea.
        """

        nit = str(
            aportante.get(
                "nit",
                "",
            ),
        ).strip()

        razon = str(
            aportante.get(
                "razon_social",
                "",
            ),
        ).strip()

        dv = str(
            aportante.get(
                "dv",
                "",
            ),
        ).strip()

        periodo = f"{anio:04d}{mes:02d}"
        directorio = cls._directorio_salida()

        ruta_tipo1 = directorio / f"AP{periodo}{nit}.txt"
        ruta_tipo2 = directorio / f"PILA{periodo}{nit}.txt"

        lineas_tipo1 = [
            cls._registro_tipo1_aportante(
                razon_social=razon,
                nit=nit,
                dv=dv,
            ),
        ]

        lineas_tipo2 = [
            cls._registro_encabezado_planilla(
                razon_social=razon,
                nit=nit,
                dv=dv,
                anio=anio,
                mes=mes,
                arl_codigo=str(
                    aportante.get(
                        "arl_codigo",
                        CODIGO_ARL_DEFECTO,
                    ),
                ),
            ),
        ]

        for indice, fila in enumerate(
            liquidaciones,
            start=1,
        ):

            lineas_tipo2.append(
                cls._registro_detalle_cotizante(
                    secuencia=indice,
                    fila=fila,
                ),
            )

        ruta_tipo1.write_text(
            "\n".join(lineas_tipo1),
            encoding="utf-8",
        )

        ruta_tipo2.write_text(
            "\n".join(lineas_tipo2),
            encoding="utf-8",
        )

        return {
            "tipo1": str(ruta_tipo1),
            "tipo2": str(ruta_tipo2),
        }
