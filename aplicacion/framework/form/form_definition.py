from __future__ import annotations

from collections.abc import Iterable

from .field import Field
from .field_group import FieldGroup
from .form_layout import FormLayout


class FormDefinition:
    """
    Describe completamente un formulario.

    No conoce:

        • Qt
        • SQLAlchemy
        • Widgets
        • CRUD

    Solo describe la estructura del formulario.
    """

    # ==================================================
    # Información
    # ==================================================

    titulo: str = ""

    descripcion: str = ""

    # ==================================================
    # Layout
    # ==================================================

    layout: FormLayout | None = None

    # ==================================================
    # Campos
    # ==================================================

    campos: tuple[Field, ...] = ()

    grupos: tuple[FieldGroup, ...] = ()

    # Tabla del listado CRUD.
    #
    # Convención NEXUS:
    # - Maestros: ``table_definition`` apunta a un ``TableDefinition``
    #   (puede vivir en ``*_table.py`` separado del formulario).
    # - Documentos comerciales: clase stub ``FormularioLista`` con
    #   ``definition`` solo para columnas; el formulario real es ``Page``.
    #
    # Ver ``docs/Framework-v1.0.md`` → Patrones CRUD.

    table_definition = None

    # ==================================================
    # Grupos
    # ==================================================

    @classmethod
    def obtener_grupos(
        cls,
    ) -> list[FieldGroup]:

        if cls.grupos:

            return list(
                cls.grupos
            )

        if cls.campos:

            return [

                FieldGroup(
                    titulo="",
                    campos=list(
                        cls.campos
                    ),
                )

            ]

        return []

    # ==================================================
    # Campos
    # ==================================================

    @classmethod
    def obtener_campos(
        cls,
    ) -> list[Field]:

        return [

            campo

            for grupo in cls.obtener_grupos()

            for campo in grupo.campos

        ]

    # ==================================================
    # Buscar campo
    # ==================================================

    @classmethod
    def buscar_campo(
        cls,
        nombre: str,
    ) -> Field | None:

        for campo in cls.obtener_campos():

            if campo.nombre == nombre:

                return campo

        return None

    # ==================================================
    # Alias
    # ==================================================

    buscar = buscar_campo

    obtener_campo = buscar_campo

    # ==================================================
    # Buscar grupo
    # ==================================================

    @classmethod
    def buscar_grupo(
        cls,
        titulo: str,
    ) -> FieldGroup | None:

        for grupo in cls.obtener_grupos():

            if grupo.titulo == titulo:

                return grupo

        return None

    # ==================================================
    # Existe
    # ==================================================

    @classmethod
    def existe(
        cls,
        nombre: str,
    ) -> bool:

        return (
            cls.buscar_campo(
                nombre
            )
            is not None
        )

    # ==================================================
    # Campos requeridos
    # ==================================================

    @classmethod
    def obligatorios(
        cls,
    ) -> list[Field]:

        return [

            campo

            for campo in cls.obtener_campos()

            if campo.requerido

        ]

    # ==================================================
    # Campos visibles
    # ==================================================

    @classmethod
    def visibles(
        cls,
    ) -> list[Field]:

        return [

            campo

            for campo in cls.obtener_campos()

            if campo.visible

        ]

    # ==================================================
    # Campos habilitados
    # ==================================================

    @classmethod
    def habilitados(
        cls,
    ) -> list[Field]:

        return [

            campo

            for campo in cls.obtener_campos()

            if campo.habilitado

        ]

    # ==================================================
    # Nombres
    # ==================================================

    @classmethod
    def nombres(
        cls,
    ) -> list[str]:

        return [

            campo.nombre

            for campo in cls.obtener_campos()

        ]

    # ==================================================
    # Iterador
    # ==================================================

    @classmethod
    def __iter__(
        cls,
    ) -> Iterable[Field]:

        return iter(
            cls.obtener_campos()
        )