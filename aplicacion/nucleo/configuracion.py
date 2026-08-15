import json
from pathlib import Path


class Configuracion:

    _datos = None

    @classmethod
    def cargar(cls):

        if cls._datos is None:

            ruta = (
                Path(__file__)
                .parent.parent.parent
                / "configuracion"
                / "configuracion.json"
            )

            with open(
                ruta,
                "r",
                encoding="utf-8"
            ) as archivo:

                cls._datos = json.load(
                    archivo
                )

        return cls._datos

    @classmethod
    def obtener(cls, *claves):

        datos = cls.cargar()

        for clave in claves:
            datos = datos.get(clave)

            if datos is None:
                return None

        return datos

    @classmethod
    def _ruta_archivo(cls) -> Path:

        return (
            Path(__file__)
            .parent.parent.parent
            / "configuracion"
            / "configuracion.json"
        )

    @classmethod
    def persistir(
        cls,
        datos: dict | None = None,
    ) -> None:

        if datos is None:

            datos = cls.cargar()

        ruta = cls._ruta_archivo()

        with open(
            ruta,
            "w",
            encoding="utf-8",
        ) as archivo:

            json.dump(
                datos,
                archivo,
                indent=4,
                ensure_ascii=False,
            )

            archivo.write("\n")

        cls._datos = datos

    @classmethod
    def actualizar(
        cls,
        claves: tuple[str, ...],
        valor,
    ) -> None:

        datos = cls.cargar()

        actual = datos

        for clave in claves[:-1]:

            siguiente = actual.get(clave)

            if not isinstance(
                siguiente,
                dict,
            ):

                siguiente = {}

                actual[clave] = siguiente

            actual = siguiente

        actual[claves[-1]] = valor

        cls.persistir(
            datos,
        )