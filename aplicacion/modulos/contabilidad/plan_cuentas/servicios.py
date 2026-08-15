from __future__ import annotations

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)
from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)

from .repositorio import RepositorioPlanCuenta

TIPOS_CUENTA = [
    ("Activo", "activo"),
    ("Pasivo", "pasivo"),
    ("Patrimonio", "patrimonio"),
    ("Ingreso", "ingreso"),
    ("Gasto", "gasto"),
]


class ServicioPlanCuenta(ServicioBase):

    repositorio = RepositorioPlanCuenta

    @classmethod
    def inicializar(cls):

        ServicioContabilidad.inicializar_plan()

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        codigo = str(
            datos.get(
                "codigo",
                "",
            ),
        ).strip()

        nombre = str(
            datos.get(
                "nombre",
                "",
            ),
        ).strip()

        if not codigo:

            raise ValueError(
                "El código es obligatorio.",
            )

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio.",
            )

        if cls.repositorio.existe_codigo(
            codigo,
            excluir_id=id_registro,
        ):

            raise ValueError(
                "Ya existe una cuenta con ese código.",
            )

        tipo = str(
            datos.get(
                "tipo",
                "activo",
            )
            or "activo",
        ).strip().lower()

        tipos_validos = {
            item[1]
            for item in TIPOS_CUENTA
        }

        if tipo not in tipos_validos:

            raise ValueError(
                "Tipo de cuenta no válido.",
            )

        datos["codigo"] = codigo
        datos["nombre"] = nombre
        datos["tipo"] = tipo
        datos["activo"] = bool(
            datos.get(
                "activo",
                True,
            ),
        )

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def buscar_para_lookup(
        cls,
        texto: str = "",
    ) -> list[LookupResult]:

        registros = cls.repositorio.buscar_para_lookup(
            texto,
        )

        return [
            LookupResult(
                valor=registro.id,
                codigo=registro.codigo,
                texto=(
                    f"{registro.codigo} — "
                    f"{registro.nombre}"
                ),
                objeto=registro,
            )
            for registro in registros
        ]
