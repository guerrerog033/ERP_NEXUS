from __future__ import annotations

from datetime import date
from pathlib import Path

from aplicacion.nucleo.configuracion import Configuracion


class ExportadorPila:

    @classmethod
    def _nit_empresa(cls) -> str:

        return str(
            Configuracion.obtener(
                "empresa",
                "nit",
            )
            or "",
        ).strip()

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
    def generar(
        cls,
        *,
        anio: int,
        mes: int,
        liquidaciones: list[dict],
    ) -> str:
        """
        Genera archivo plano simplificado de PILA (referencia operativa).
        """

        nit = cls._nit_empresa()
        periodo = f"{anio:04d}{mes:02d}"
        nombre = f"PILA_{periodo}_{nit or 'EMPRESA'}.txt"
        ruta = cls._directorio_salida() / nombre

        lineas = [
            f"ENC;{nit};{periodo};{date.today().isoformat()}",
            "TIPDOC;NUMDOC;IBC;SALUD_EMP;PENSION_EMP;SALUD_PAT;PENSION_PAT;FSP",
        ]

        for fila in liquidaciones:

            lineas.append(
                ";".join(
                    [
                        str(
                            fila.get(
                                "tipo_documento",
                                "CC",
                            ),
                        ),
                        str(
                            fila.get(
                                "numero_documento",
                                "",
                            ),
                        ),
                        str(
                            int(
                                float(
                                    fila.get(
                                        "ibc",
                                        0,
                                    )
                                    or 0,
                                ),
                            ),
                        ),
                        str(
                            int(
                                float(
                                    fila.get(
                                        "salud_empleado",
                                        0,
                                    )
                                    or 0,
                                ),
                            ),
                        ),
                        str(
                            int(
                                float(
                                    fila.get(
                                        "pension_empleado",
                                        0,
                                    )
                                    or 0,
                                ),
                            ),
                        ),
                        str(
                            int(
                                float(
                                    fila.get(
                                        "salud_patronal",
                                        0,
                                    )
                                    or 0,
                                ),
                            ),
                        ),
                        str(
                            int(
                                float(
                                    fila.get(
                                        "pension_patronal",
                                        0,
                                    )
                                    or 0,
                                ),
                            ),
                        ),
                        str(
                            int(
                                float(
                                    fila.get(
                                        "fsp",
                                        0,
                                    )
                                    or 0,
                                ),
                            ),
                        ),
                    ],
                ),
            )

        ruta.write_text(
            "\n".join(lineas),
            encoding="utf-8",
        )

        return str(ruta)

    @classmethod
    def generar_aportes_en_linea(
        cls,
        *,
        anio: int,
        mes: int,
        aportante: dict,
        liquidaciones: list[dict],
    ) -> dict[str, str]:

        from .pila_aportes import (
            ExportadorPilaAportesEnLinea,
        )

        return ExportadorPilaAportesEnLinea.generar(
            anio=anio,
            mes=mes,
            aportante=aportante,
            liquidaciones=liquidaciones,
        )
