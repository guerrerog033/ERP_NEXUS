from sqlalchemy import or_

from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.framework.datagrid.filtros import (
    FiltroConsulta,
)

from .constantes import TIPO_A_ROL
from .modelos import (
    Tercero,
    TerceroContacto,
    TerceroCuentaBancaria,
    TerceroDireccion,
)


class TerceroRepositorio(RepositorioBase):

    modelo = Tercero

    _ORDEN_DEFAULT = (
        Tercero.razon_social,
        Tercero.primer_apellido,
        Tercero.primer_nombre,
    )

    @classmethod
    def _filtro_tipo_tercero(
        cls,
        consulta,
        tipo_tercero: str,
    ):

        campo_rol = TIPO_A_ROL.get(
            tipo_tercero,
        )

        if not campo_rol:

            return consulta.filter(
                cls.modelo.tipo_tercero
                == tipo_tercero,
            )

        return consulta.filter(
            or_(
                getattr(
                    cls.modelo,
                    campo_rol,
                ).is_(True),
                cls.modelo.tipo_tercero
                == tipo_tercero,
            ),
        )

    @classmethod
    def _aplicar_busqueda_texto(
        cls,
        consulta,
        texto: str,
    ):

        patron = f"%{texto.strip()}%"

        return consulta.filter(
            or_(
                cls.modelo.numero_documento.ilike(
                    patron,
                ),
                cls.modelo.razon_social.ilike(
                    patron,
                ),
                cls.modelo.nombre_comercial.ilike(
                    patron,
                ),
                cls.modelo.primer_nombre.ilike(
                    patron,
                ),
                cls.modelo.segundo_nombre.ilike(
                    patron,
                ),
                cls.modelo.primer_apellido.ilike(
                    patron,
                ),
                cls.modelo.segundo_apellido.ilike(
                    patron,
                ),
                cls.modelo.correo.ilike(
                    patron,
                ),
                cls.modelo.ciudad.ilike(
                    patron,
                ),
            )
        )

    @classmethod
    def consultar(
        cls,
        *,
        pagina: int = 1,
        por_pagina: int = 50,
        ordenar_por=None,
        filtros=None,
        texto: str | None = None,
        tipo_tercero: str | None = None,
    ):

        filtros_combinados = list(
            filtros or [],
        )

        if tipo_tercero:

            filtros_combinados.append(
                FiltroConsulta(
                    campo="tipo_tercero",
                    operador="eq",
                    valor=tipo_tercero,
                ),
            )

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            consulta = db.query(
                cls.modelo,
            )

            if texto:

                consulta = cls._aplicar_busqueda_texto(
                    consulta,
                    texto,
                )

            for filtro in filtros_combinados:

                consulta = cls._aplicar_filtro(
                    consulta,
                    filtro,
                )

            total = consulta.count()

            if ordenar_por is None:

                ordenar_por = cls._ORDEN_DEFAULT

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

    # =====================================================
    # Buscar por documento
    # =====================================================

    @classmethod
    def obtener_por_documento(
        cls,
        tipo_documento,
        numero_documento,
    ):

        db = cls.obtener_sesion()

        try:

            return (

                db.query(cls.modelo)

                .filter(

                    cls.modelo.tipo_documento == tipo_documento,

                    cls.modelo.numero_documento == numero_documento,

                )

                .first()

            )

        finally:

            db.close()

    @classmethod
    def obtener_por_tipo(
        cls,
        tipo_tercero,
    ):

        db = cls.obtener_sesion()

        try:

            return (

                cls._filtro_tipo_tercero(
                    db.query(cls.modelo),
                    tipo_tercero,
                )

                .order_by(
                    cls.modelo.razon_social,
                    cls.modelo.primer_apellido,
                    cls.modelo.primer_nombre,
                )

                .all()

            )

        finally:

            db.close()

    @classmethod
    def buscar(
        cls,
        texto,
        tipo_tercero=None,
    ):

        db = cls.obtener_sesion()

        try:

            consulta = db.query(
                cls.modelo,
            )

            if tipo_tercero:

                consulta = cls._filtro_tipo_tercero(
                    consulta,
                    tipo_tercero,
                )

            patron = f"%{texto.strip()}%"

            consulta = consulta.filter(
                or_(
                    cls.modelo.numero_documento.ilike(
                        patron,
                    ),
                    cls.modelo.razon_social.ilike(
                        patron,
                    ),
                    cls.modelo.nombre_comercial.ilike(
                        patron,
                    ),
                    cls.modelo.primer_nombre.ilike(
                        patron,
                    ),
                    cls.modelo.segundo_nombre.ilike(
                        patron,
                    ),
                    cls.modelo.primer_apellido.ilike(
                        patron,
                    ),
                    cls.modelo.segundo_apellido.ilike(
                        patron,
                    ),
                    cls.modelo.correo.ilike(
                        patron,
                    ),
                    cls.modelo.ciudad.ilike(
                        patron,
                    ),
                )
            )

            return consulta.order_by(
                cls.modelo.razon_social,
                cls.modelo.primer_apellido,
            ).all()

        finally:

            db.close()


class _RepositorioRegistroTercero(RepositorioBase):
    """
    Base para los registros hijos de un tercero (direcciones,
    contactos, cuentas bancarias): mismo CRUD genérico, más un
    listado filtrado por ``tercero_id``.
    """

    @classmethod
    def listar_por_tercero(
        cls,
        tercero_id: int,
    ) -> list:

        db = cls.obtener_sesion()

        try:

            return (
                db.query(
                    cls.modelo,
                )
                .filter(
                    cls.modelo.tercero_id == tercero_id,
                )
                .order_by(
                    cls.modelo.principal.desc(),
                    cls.modelo.id,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def limpiar_principal(
        cls,
        tercero_id: int,
        excluir_id: int | None = None,
    ) -> None:

        db = cls.obtener_sesion()

        try:

            consulta = db.query(
                cls.modelo,
            ).filter(
                cls.modelo.tercero_id == tercero_id,
                cls.modelo.principal.is_(True),
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    cls.modelo.id != excluir_id,
                )

            for registro in consulta.all():

                registro.principal = False

            db.commit()

        finally:

            db.close()


class TerceroDireccionRepositorio(_RepositorioRegistroTercero):

    modelo = TerceroDireccion


class TerceroContactoRepositorio(_RepositorioRegistroTercero):

    modelo = TerceroContacto


class TerceroCuentaBancariaRepositorio(_RepositorioRegistroTercero):

    modelo = TerceroCuentaBancaria
