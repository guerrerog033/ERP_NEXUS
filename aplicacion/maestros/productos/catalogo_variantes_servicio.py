from __future__ import annotations

from aplicacion.base_datos.conexion import (
    SessionLocal,
)
from aplicacion.maestros.productos.modelos import (
    CatalogoVariante,
)


TIPOS_VARIANTE = {
    "talla": "Talla",
    "color": "Color",
    "calibre": "Calibre",
    "largo": "Largo",
}

PREDETERMINADOS = {
    "talla": [
        "XS",
        "S",
        "M",
        "L",
        "XL",
        "XXL",
    ],
    "color": [
        "Negro",
        "Blanco",
        "Azul",
        "Rojo",
        "Verde",
        "Gris",
    ],
    "calibre": [
        "38",
        "40",
        "42",
        "44",
        "46",
    ],
    "largo": [
        "Corto",
        "Regular",
        "Largo",
    ],
}


class ServicioCatalogoVariantes:

    @classmethod
    def asegurar_predeterminados(
        cls,
    ) -> None:

        db = SessionLocal()

        try:

            for tipo, valores in PREDETERMINADOS.items():

                for orden, valor in enumerate(
                    valores,
                ):

                    existe = (
                        db.query(
                            CatalogoVariante,
                        )
                        .filter(
                            CatalogoVariante.tipo
                            == tipo,
                            CatalogoVariante.nombre_tipo
                            == "",
                            CatalogoVariante.valor
                            == valor,
                        )
                        .first()
                    )

                    if existe is not None:

                        continue

                    db.add(
                        CatalogoVariante(
                            tipo=tipo,
                            nombre_tipo="",
                            valor=valor,
                            orden=orden,
                            activo=True,
                        ),
                    )

            db.commit()

        finally:

            db.close()

    @classmethod
    def listar_por_tipo(
        cls,
        tipo: str,
        *,
        nombre_tipo: str = "",
    ) -> list[CatalogoVariante]:

        cls.asegurar_predeterminados()

        db = SessionLocal()

        try:

            return (
                db.query(
                    CatalogoVariante,
                )
                .filter(
                    CatalogoVariante.tipo
                    == tipo,
                    CatalogoVariante.nombre_tipo
                    == (
                        nombre_tipo or ""
                    ),
                    CatalogoVariante.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    CatalogoVariante.orden,
                    CatalogoVariante.valor,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def listar_valores(
        cls,
        tipo: str,
        *,
        nombre_tipo: str = "",
    ) -> list[str]:

        return [
            item.valor
            for item in cls.listar_por_tipo(
                tipo,
                nombre_tipo=nombre_tipo,
            )
        ]

    @classmethod
    def listar_tipos_atributo(
        cls,
    ) -> list[str]:

        cls.asegurar_predeterminados()

        db = SessionLocal()

        try:

            filas = (
                db.query(
                    CatalogoVariante.nombre_tipo,
                )
                .filter(
                    CatalogoVariante.tipo
                    == "atributo",
                    CatalogoVariante.nombre_tipo
                    != "",
                    CatalogoVariante.activo.is_(
                        True,
                    ),
                )
                .distinct()
                .order_by(
                    CatalogoVariante.nombre_tipo,
                )
                .all()
            )

            return [
                fila[0]
                for fila in filas
            ]

        finally:

            db.close()

    @classmethod
    def listar_todos(
        cls,
        tipo: str | None = None,
    ) -> list[CatalogoVariante]:

        cls.asegurar_predeterminados()

        db = SessionLocal()

        try:

            consulta = db.query(
                CatalogoVariante,
            )

            if tipo:

                consulta = consulta.filter(
                    CatalogoVariante.tipo
                    == tipo,
                )

            return consulta.order_by(
                CatalogoVariante.tipo,
                CatalogoVariante.nombre_tipo,
                CatalogoVariante.orden,
                CatalogoVariante.valor,
            ).all()

        finally:

            db.close()

    @classmethod
    def crear_tipo_atributo(
        cls,
        nombre: str,
    ) -> tuple[bool, str]:

        nombre = str(
            nombre or "",
        ).strip()

        if not nombre:

            return (
                False,
                "Indique el nombre del atributo.",
            )

        existentes = cls.listar_por_tipo(
            "atributo",
            nombre_tipo=nombre,
        )

        if existentes:

            return (
                False,
                "Ese atributo ya existe.",
            )

        return cls.crear(
            "atributo",
            "General",
            nombre_tipo=nombre,
        )

    @classmethod
    def crear(
        cls,
        tipo: str,
        valor: str,
        *,
        nombre_tipo: str = "",
    ) -> tuple[bool, str]:

        valor = str(
            valor or "",
        ).strip()

        if not valor:

            return (
                False,
                "Indique un valor.",
            )

        tipo = str(
            tipo or "",
        ).strip().lower()

        nombre_tipo = str(
            nombre_tipo or "",
        ).strip()

        if (
            tipo == "atributo"
            and not nombre_tipo
        ):

            return (
                False,
                "Indique el nombre del atributo.",
            )

        db = SessionLocal()

        try:

            duplicado = (
                db.query(
                    CatalogoVariante,
                )
                .filter(
                    CatalogoVariante.tipo
                    == tipo,
                    CatalogoVariante.nombre_tipo
                    == nombre_tipo,
                    CatalogoVariante.valor
                    == valor,
                )
                .first()
            )

            if duplicado is not None:

                return (
                    False,
                    "Ese valor ya existe.",
                )

            max_orden = (
                db.query(
                    CatalogoVariante,
                )
                .filter(
                    CatalogoVariante.tipo
                    == tipo,
                    CatalogoVariante.nombre_tipo
                    == nombre_tipo,
                )
                .count()
            )

            db.add(
                CatalogoVariante(
                    tipo=tipo,
                    nombre_tipo=nombre_tipo,
                    valor=valor,
                    orden=max_orden,
                    activo=True,
                ),
            )

            db.commit()

        finally:

            db.close()

        return (
            True,
            "",
        )

    @classmethod
    def eliminar(
        cls,
        item_id: int,
    ) -> None:

        db = SessionLocal()

        try:

            item = db.get(
                CatalogoVariante,
                item_id,
            )

            if item is None:

                return

            db.delete(
                item,
            )

            db.commit()

        finally:

            db.close()

    @classmethod
    def etiqueta_tipo(
        cls,
        tipo: str,
        nombre_tipo: str = "",
    ) -> str:

        if tipo == "atributo":

            return (
                nombre_tipo
                or "Atributo"
            )

        return TIPOS_VARIANTE.get(
            tipo,
            tipo.capitalize(),
        )
