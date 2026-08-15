from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from aplicacion.autenticacion.modelos import Rol, Usuario
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase


class RepositorioUsuario(RepositorioBase):

    modelo = Usuario

    @classmethod
    def _consulta_con_rol(
        cls,
        db,
    ):

        return db.query(
            Usuario,
        ).options(
            joinedload(
                Usuario.rol,
            ),
        )

    @classmethod
    def consultar(
        cls,
        *,
        pagina: int = 1,
        por_pagina: int = 50,
        ordenar_por=None,
        filtros=None,
    ):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            consulta = cls._consulta_con_rol(
                db,
            )

            for filtro in (
                filtros or [],
            ):

                consulta = cls._aplicar_filtro(
                    consulta,
                    filtro,
                )

            total = consulta.count()

            if ordenar_por is not None:

                consulta = consulta.order_by(
                    *ordenar_por,
                )

            pagina = max(
                1,
                pagina,
            )

            por_pagina = max(
                1,
                por_pagina,
            )

            registros = (
                consulta.offset(
                    (
                        pagina
                        - 1
                    )
                    * por_pagina,
                )
                .limit(
                    por_pagina,
                )
                .all()
            )

            return {
                "registros": registros,
                "total": total,
                "pagina": pagina,
                "por_pagina": por_pagina,
            }

        finally:

            db.close()

    @classmethod
    def obtener_todos(
        cls,
        ordenar_por=None,
    ):

        db = SessionLocal()

        try:

            return (
                cls._consulta_con_rol(
                    db,
                )
                .order_by(
                    Usuario.usuario,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def obtener_por_id(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            return (
                cls._consulta_con_rol(
                    db,
                )
                .filter(
                    Usuario.id == id_registro,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def buscar(
        cls,
        texto,
    ):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                cls._consulta_con_rol(
                    db,
                )
                .filter(
                    or_(
                        Usuario.usuario.ilike(
                            f"%{texto}%",
                        ),
                        Usuario.nombre.ilike(
                            f"%{texto}%",
                        ),
                        Usuario.correo.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    Usuario.usuario,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_usuario(
        cls,
        usuario: str,
        excluir_id=None,
    ) -> bool:

        db = SessionLocal()

        try:

            consulta = (
                db.query(Usuario)
                .filter(
                    Usuario.usuario == usuario,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Usuario.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def contar_por_rol(
        cls,
        rol_id: int,
    ) -> int:

        db = SessionLocal()

        try:

            return (
                db.query(Usuario)
                .filter(
                    Usuario.rol_id == rol_id,
                    Usuario.activo.is_(True),
                )
                .count()
            )

        finally:

            db.close()

    @classmethod
    def contar_admins_activos(
        cls,
        excluir_id=None,
    ) -> int:

        db = SessionLocal()

        try:

            consulta = (
                db.query(Usuario)
                .join(Rol)
                .filter(
                    Rol.codigo == "admin",
                    Usuario.activo.is_(True),
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Usuario.id != excluir_id,
                )

            return consulta.count()

        finally:

            db.close()

    @classmethod
    def guardar(
        cls,
        datos,
    ):

        db = SessionLocal()

        try:

            registro = Usuario(
                **datos,
            )

            db.add(registro)
            db.commit()
            db.refresh(registro)

            return cls.obtener_por_id(
                registro.id,
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar(
        cls,
        id_registro,
        datos,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(Usuario)
                .filter(
                    Usuario.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            for campo, valor in datos.items():

                setattr(
                    registro,
                    campo,
                    valor,
                )

            db.commit()

            return cls.obtener_por_id(
                id_registro,
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
