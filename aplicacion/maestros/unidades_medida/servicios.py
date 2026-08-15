from aplicacion.comunes.servicio_base import ServicioBase

from .repositorio import UnidadMedidaRepositorio


# Códigos UN/CEFACT (Recomendación 20) que la DIAN referencia en su
# Anexo Técnico de factura electrónica para las unidades de medida
# más comunes. Verificar contra la versión vigente del Anexo Técnico
# antes de emitir en producción — DIAN puede ajustar el catálogo.
UNIDADES_PREDETERMINADAS = (
    ("Und", "Unidad", "94"),
    ("Par", "Par", "PR"),
    ("Caja", "Caja", "XBX"),
    ("Pq", "Paquete", "PK"),
    ("Mts", "Metro", "MTR"),
    ("Gls", "Galón", "GLL"),
    ("Lts", "Litro", "LTR"),
)


class ServicioUnidadMedida(ServicioBase):

    repositorio = UnidadMedidaRepositorio

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
            )
        ).strip()

        nombre = str(
            datos.get(
                "nombre",
                "",
            )
        ).strip()

        if not codigo:

            raise ValueError(
                "El código es obligatorio."
            )

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio."
            )

        if cls.repositorio.existe_codigo(
            codigo,
            id_registro,
        ):

            raise ValueError(
                "Ya existe una unidad de medida con ese código."
            )

        datos["codigo"] = codigo
        datos["nombre"] = nombre

        datos["codigo_dian"] = str(
            datos.get(
                "codigo_dian",
                "",
            )
            or ""
        ).strip()

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto
        )

    @classmethod
    def inicializar_predeterminados(cls) -> None:

        for (
            codigo,
            nombre,
            codigo_dian,
        ) in UNIDADES_PREDETERMINADAS:

            if cls.repositorio.existe_codigo(
                codigo,
            ):

                continue

            cls.repositorio.guardar(
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "codigo_dian": codigo_dian,
                    "activo": True,
                }
            )
