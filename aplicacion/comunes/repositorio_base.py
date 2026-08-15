from aplicacion.base_datos.conexion import SessionLocal


class RepositorioBase:

    modelo = None

    @classmethod
    def _validar_modelo(cls):
        if cls.modelo is None:
            raise ValueError(
                f"{cls.__name__} debe definir la variable 'modelo'."
            )

    @classmethod
    def _aplicar_filtro(
        cls,
        consulta,
        filtro,
    ):

        from aplicacion.framework.datagrid.filtros import (
            FiltroConsulta,
        )

        if not isinstance(
            filtro,
            FiltroConsulta,
        ):

            return consulta

        columna = getattr(
            cls.modelo,
            filtro.campo,
            None,
        )

        if columna is None:

            return consulta

        if filtro.operador == "eq":

            return consulta.filter(
                columna
                == filtro.valor,
            )

        if filtro.operador == "like":

            return consulta.filter(
                columna.ilike(
                    filtro.valor,
                ),
            )

        if filtro.operador == "gte":

            return consulta.filter(
                columna
                >= filtro.valor,
            )

        if filtro.operador == "lte":

            return consulta.filter(
                columna
                <= filtro.valor,
            )

        return consulta

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

            consulta = db.query(
                cls.modelo,
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
    def obtener_sesion(cls):
        return SessionLocal()

    @classmethod
    def obtener_todos(cls, ordenar_por=None):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            consulta = db.query(cls.modelo)

            if ordenar_por is not None:
                consulta = consulta.order_by(*ordenar_por)

            return consulta.all()

        finally:
            db.close()

    @classmethod
    def obtener_por_id(cls, id_registro):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            return (
                db.query(cls.modelo)
                .filter(cls.modelo.id == id_registro)
                .first()
            )

        finally:
            db.close()

    @classmethod
    def obtener_primero(cls):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            return (
                db.query(cls.modelo)
                .first()
            )

        finally:
            db.close()

    @classmethod
    def contar(cls):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            return (
                db.query(cls.modelo)
                .count()
            )

        finally:
            db.close()

    @classmethod
    def existe(cls, id_registro):

        return (
            cls.obtener_por_id(id_registro)
            is not None
        )

    @classmethod
    def guardar(cls, datos):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            registro = cls.modelo(**datos)

            db.add(registro)

            db.commit()

            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar(cls, id_registro, datos):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            registro = (
                db.query(cls.modelo)
                .filter(cls.modelo.id == id_registro)
                .first()
            )

            if registro is None:
                return None

            for campo, valor in datos.items():
                setattr(registro, campo, valor)

            db.commit()

            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def eliminar(cls, id_registro):

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            registro = (
                db.query(cls.modelo)
                .filter(cls.modelo.id == id_registro)
                .first()
            )

            if registro is None:
                return False

            db.delete(registro)

            db.commit()

            return True

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()