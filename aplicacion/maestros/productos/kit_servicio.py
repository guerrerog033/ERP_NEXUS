from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from .kit_repositorio import ProductoKitComponenteRepositorio
from .repositorio import RepositorioProducto


@dataclass(slots=True)
class ComponenteExpandido:
    """
    Un componente de kit ya resuelto a producto real, con la
    cantidad total que corresponde a la cantidad de kits vendida
    (cantidad_unitaria del componente × cantidad de kits).
    """

    producto_id: int
    producto: object
    cantidad_unitaria: float
    cantidad_total: float


class ServicioProductoKit:

    repositorio = ProductoKitComponenteRepositorio

    @classmethod
    def listar_componentes(cls, kit_id: int) -> list:
        """
        Devuelve los componentes del kit ya enriquecidos con el
        código/nombre del producto (para mostrar en tablas sin
        navegar la relación componente — la fila de
        ProductoKitComponente viene de una sesión ya cerrada).
        """

        filas = cls.repositorio.listar_por_kit(
            kit_id,
        )

        resultado = []

        for fila in filas:

            producto = RepositorioProducto.obtener_por_id(
                fila.componente_id,
            )

            resultado.append(
                SimpleNamespace(
                    id=fila.id,
                    kit_id=fila.kit_id,
                    componente_id=fila.componente_id,
                    cantidad=fila.cantidad,
                    componente_codigo=(
                        producto.codigo if producto else ""
                    ),
                    componente_nombre=(
                        producto.nombre if producto else ""
                    ),
                ),
            )

        return resultado

    @classmethod
    def listar(cls, kit_id: int) -> list:
        """
        Alias de listar_componentes(): ListaRegistrosWidget (ver
        aplicacion.framework.ui.lista_registros_widget) espera la
        interfaz genérica listar/guardar/actualizar/eliminar en
        cualquier servicio que respalde una de sus listas.
        """

        return cls.listar_componentes(
            kit_id,
        )

    @classmethod
    def _validar(
        cls,
        datos: dict,
        id_registro: int | None = None,
    ) -> None:

        kit_id = datos.get("kit_id")
        componente_id = datos.get("componente_id")

        if not kit_id:

            raise ValueError(
                "Falta el kit al que pertenece el componente.",
            )

        if not componente_id:

            raise ValueError(
                "Debe seleccionar un producto componente.",
            )

        if int(kit_id) == int(componente_id):

            raise ValueError(
                "Un kit no puede tener como componente a sí mismo.",
            )

        componente = RepositorioProducto.obtener_por_id(
            componente_id,
        )

        if componente is None:

            raise ValueError(
                "El producto componente seleccionado no existe.",
            )

        if componente.es_kit:

            raise ValueError(
                "Un componente no puede ser a su vez un kit "
                "(no se admiten kits anidados).",
            )

        try:

            cantidad = float(
                datos.get(
                    "cantidad",
                    0,
                )
                or 0,
            )

        except (
            TypeError,
            ValueError,
        ):

            cantidad = 0

        if cantidad <= 0:

            raise ValueError(
                "La cantidad del componente debe ser mayor a cero.",
            )

        datos["cantidad"] = cantidad

        if cls.repositorio.existe_componente(
            kit_id,
            componente_id,
            excluir_id=id_registro,
        ):

            raise ValueError(
                "Ese producto ya está agregado como componente "
                "de este kit.",
            )

    @classmethod
    def guardar(cls, datos: dict):

        cls._validar(
            datos,
        )

        return cls.repositorio.guardar(
            datos,
        )

    @classmethod
    def actualizar(cls, id_registro: int, datos: dict):

        cls._validar(
            datos,
            id_registro,
        )

        return cls.repositorio.actualizar(
            id_registro,
            datos,
        )

    @classmethod
    def eliminar(cls, id_registro: int) -> None:

        cls.repositorio.eliminar(
            id_registro,
        )

    @classmethod
    def expandir(
        cls,
        kit_id: int,
        cantidad: float = 1,
    ) -> list[ComponenteExpandido]:
        """
        Resuelve un kit en sus componentes reales, multiplicados
        por la cantidad de kits vendida/consumida. Núcleo
        reutilizable: cualquier módulo que necesite saber "qué
        consume vender N de este kit" llama aquí, en vez de
        reimplementar la expansión.
        """

        componentes = cls.listar_componentes(
            kit_id,
        )

        resultado = []

        for componente in componentes:

            producto = RepositorioProducto.obtener_por_id(
                componente.componente_id,
            )

            if producto is None:

                continue

            cantidad_unitaria = float(
                componente.cantidad or 0,
            )

            resultado.append(
                ComponenteExpandido(
                    producto_id=producto.id,
                    producto=producto,
                    cantidad_unitaria=cantidad_unitaria,
                    cantidad_total=(
                        cantidad_unitaria * float(cantidad)
                    ),
                ),
            )

        return resultado
