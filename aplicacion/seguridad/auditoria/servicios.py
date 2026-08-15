from __future__ import annotations

from .repositorio import RepositorioAuditoria


class ServicioAuditoria:

    @classmethod
    def listar(
        cls,
        **filtros,
    ):

        return RepositorioAuditoria.listar(
            **filtros,
        )

    @classmethod
    def contar(cls) -> int:

        return RepositorioAuditoria.contar()
