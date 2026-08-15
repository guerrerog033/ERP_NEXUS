from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)
from aplicacion.maestros.listas_precio.servicios import (
    ServicioListaPrecio,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioProducto

if TYPE_CHECKING:
    from PySide6.QtGui import QPixmap


RUTA_IMAGENES = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "recursos"
    / "imagenes"
    / "productos"
)

CAMPOS_PRODUCTO = {
    "codigo",
    "codigo_barras",
    "nombre",
    "descripcion",
    "tipo",
    "unidad_medida_id",
    "categoria_id",
    "marca_id",
    "precio_venta",
    "precio_incluye_iva",
    "costo",
    "existencia",
    "stock_minimo",
    "impuesto_venta_id",
    "impuesto_compra_id",
    "imagen",
    "activo",
    "maneja_variantes",
    "atributos_variante",
}


class ServicioProducto(ServicioBase):

    repositorio = RepositorioProducto

    @classmethod
    def codigo_automatico_habilitado(cls) -> bool:

        return bool(
            Configuracion.obtener(
                "productos",
                "codigo_automatico",
            )
        )

    @classmethod
    def generar_codigo(cls) -> str:

        prefijo = (
            Configuracion.obtener(
                "productos",
                "prefijo",
            )
            or "PRD"
        )

        longitud = int(
            Configuracion.obtener(
                "productos",
                "longitud_secuencia",
            )
            or 6
        )

        secuencia = cls.repositorio.siguiente_secuencia(
            prefijo,
        )

        return (
            f"{prefijo}"
            f"{secuencia:0{longitud}d}"
        )

    @classmethod
    def _guardar_imagen(
        cls,
        archivo_origen: str,
        codigo: str,
        imagen_actual: str | None = None,
    ) -> str:

        origen = Path(archivo_origen)

        if not origen.is_file():

            return imagen_actual or ""

        RUTA_IMAGENES.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = origen.suffix.lower() or ".jpg"

        nombre = f"{codigo}{extension}"

        destino = RUTA_IMAGENES / nombre

        shutil.copy2(
            origen,
            destino,
        )

        return f"productos/{nombre}"

    @classmethod
    def _normalizar_impuesto(
        cls,
        datos,
        campo,
    ):

        valor = datos.get(
            campo,
        )

        if valor in {
            "",
            None,
        }:

            datos[campo] = None

            return

        datos[campo] = int(valor)

    @classmethod
    def _filtrar_datos_producto(
        cls,
        datos,
    ) -> dict:

        return {
            clave: datos[clave]
            for clave in CAMPOS_PRODUCTO
            if clave in datos
        }

    @classmethod
    def _sincronizar_precio_base(
        cls,
        datos,
        precios: list[dict],
    ) -> list[dict]:

        lista = ServicioListaPrecio.obtener_predeterminada()

        if lista is None:

            return precios

        precio_base = float(
            datos.get(
                "precio_venta",
                0,
            )
            or 0,
        )

        actualizado = False

        for item in precios:

            if item["lista_precio_id"] == lista.id:

                item["precio"] = precio_base

                if datos.get(
                    "impuesto_venta_id",
                ):

                    item["impuesto_id"] = datos[
                        "impuesto_venta_id"
                    ]

                actualizado = True

                break

        if not actualizado and precio_base >= 0:

            fila = {
                "lista_precio_id": lista.id,
                "precio": precio_base,
            }

            if datos.get(
                "impuesto_venta_id",
            ):

                fila["impuesto_id"] = datos[
                    "impuesto_venta_id"
                ]

            precios.append(
                fila,
            )

        return precios

    @classmethod
    def _validar_precios(
        cls,
        precios,
    ) -> list[dict]:

        filas = []

        listas_vistas = set()

        for item in precios:

            lista_precio_id = item.get(
                "lista_precio_id",
            )

            if not lista_precio_id:

                continue

            lista_precio_id = int(
                lista_precio_id,
            )

            if lista_precio_id in listas_vistas:

                raise ValueError(
                    "No repita la misma lista de precio.",
                )

            listas_vistas.add(
                lista_precio_id,
            )

            try:

                precio = float(
                    item.get(
                        "precio",
                        0,
                    )
                    or 0,
                )

            except (
                TypeError,
                ValueError,
            ):

                precio = 0.0

            if precio < 0:

                raise ValueError(
                    "El precio de lista no puede ser negativo.",
                )

            filas.append(
                {
                    "lista_precio_id": lista_precio_id,
                    "precio": precio,
                    "impuesto_id": item.get(
                        "impuesto_id",
                    ),
                },
            )

        return filas

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

        if (
            not codigo
            and cls.codigo_automatico_habilitado()
            and id_registro is None
        ):

            codigo = cls.generar_codigo()

        if not codigo:

            raise ValueError(
                "El código es obligatorio.",
            )

        nombre = str(
            datos.get(
                "nombre",
                "",
            )
        ).strip()

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio.",
            )

        if cls.repositorio.existe_codigo(
            codigo.upper(),
            id_registro,
        ):

            raise ValueError(
                "Ya existe un producto con ese código.",
            )

        codigo_barras = str(
            datos.get(
                "codigo_barras",
                "",
            )
            or "",
        ).strip()

        if codigo_barras and cls.repositorio.existe_codigo_barras(
            codigo_barras,
            id_registro,
        ):

            raise ValueError(
                "Ya existe un producto con ese código de barras.",
            )

        datos["codigo"] = codigo.upper()
        datos["nombre"] = nombre
        datos["codigo_barras"] = (
            codigo_barras
            or None
        )

        descripcion = datos.get(
            "descripcion",
            "",
        )

        datos["descripcion"] = str(
            descripcion,
        ).strip()

        tipo = str(
            datos.get(
                "tipo",
                "producto",
            )
        ).strip().lower()

        if tipo not in {
            "producto",
            "servicio",
        }:

            tipo = "producto"

        datos["tipo"] = tipo

        from aplicacion.maestros.unidades_medida.repositorio import (
            UnidadMedidaRepositorio,
        )

        unidad_medida_id = datos.get(
            "unidad_medida_id",
        )

        if unidad_medida_id:

            if UnidadMedidaRepositorio.obtener_por_id(
                unidad_medida_id,
            ) is None:

                raise ValueError(
                    "La unidad de medida seleccionada no existe.",
                )

        else:

            unidad_defecto = UnidadMedidaRepositorio.obtener_por_codigo(
                "Und",
            )

            unidad_medida_id = (
                unidad_defecto.id
                if unidad_defecto is not None
                else None
            )

        datos["unidad_medida_id"] = unidad_medida_id

        for campo in (
            "precio_venta",
            "costo",
        ):

            valor = datos.get(
                campo,
                0,
            )

            try:

                datos[campo] = float(
                    valor or 0,
                )

            except (
                TypeError,
                ValueError,
            ):

                datos[campo] = 0.0

        datos["precio_incluye_iva"] = bool(
            datos.get(
                "precio_incluye_iva",
                False,
            )
        )

        datos["maneja_variantes"] = bool(
            datos.get(
                "maneja_variantes",
                False,
            )
        )

        for campo in (
            "existencia",
            "stock_minimo",
        ):

            valor = datos.get(
                campo,
                0,
            )

            try:

                datos[campo] = max(
                    0.0,
                    float(
                        valor or 0,
                    ),
                )

            except (
                TypeError,
                ValueError,
            ):

                datos[campo] = 0.0

        if datos["tipo"] == "servicio":

            datos["existencia"] = 0.0
            datos["stock_minimo"] = 0.0

        if datos["maneja_variantes"]:

            datos["existencia"] = 0.0

        cls._normalizar_impuesto(
            datos,
            "impuesto_venta_id",
        )

        cls._normalizar_impuesto(
            datos,
            "impuesto_compra_id",
        )

        archivo_imagen = datos.pop(
            "_imagen_archivo",
            None,
        )

        if archivo_imagen:

            datos["imagen"] = cls._guardar_imagen(
                archivo_imagen,
                datos["codigo"],
                datos.get("imagen"),
            )

        elif "imagen" not in datos:

            datos["imagen"] = ""

        datos.pop(
            "_imagen_archivo",
            None,
        )

    @classmethod
    def _definiciones_atributos_producto(
        cls,
        producto,
    ) -> list[dict]:

        from aplicacion.maestros.productos.atributos_variante_widget import (
            normalizar_clave_atributo,
        )

        raw = getattr(
            producto,
            "atributos_variante",
            None,
        ) or []

        definiciones = []

        for item in raw:

            if isinstance(
                item,
                dict,
            ):

                nombre = str(
                    item.get(
                        "nombre",
                        "",
                    )
                ).strip()

                if not nombre:

                    continue

                clave = str(
                    item.get(
                        "clave",
                        "",
                    )
                ).strip() or normalizar_clave_atributo(
                    nombre,
                )

            else:

                nombre = str(
                    item or "",
                ).strip()

                if not nombre:

                    continue

                clave = normalizar_clave_atributo(
                    nombre,
                )

            definiciones.append(
                {
                    "nombre": nombre,
                    "clave": clave,
                },
            )

        return definiciones

    @classmethod
    def _etiqueta_variante(
        cls,
        variante,
        *,
        incluir_stock: bool = True,
    ) -> str:

        partes = []

        for etiqueta, valor in (
            ("Talla", variante.talla),
            ("Color", variante.color),
            ("Calibre", variante.calibre),
            ("Largo", variante.largo),
        ):

            texto = str(
                valor or "",
            ).strip()

            if texto:

                partes.append(
                    f"{etiqueta} {texto}",
                )

        atributos = getattr(
            variante,
            "atributos",
            None,
        ) or {}

        if isinstance(
            atributos,
            dict,
        ):

            for clave, valor in atributos.items():

                texto = str(
                    valor or "",
                ).strip()

                if texto:

                    etiqueta = str(
                        clave,
                    ).replace(
                        "_",
                        " ",
                    ).capitalize()

                    partes.append(
                        f"{etiqueta} {texto}",
                    )

        if incluir_stock:

            existencia = float(
                getattr(
                    variante,
                    "existencia",
                    0,
                )
                or 0,
            )

            partes.append(
                f"Stock {existencia:g}",
            )

        return " · ".join(
            partes,
        )

    @classmethod
    def _validar_variantes(
        cls,
        variantes: list[dict],
        codigo_producto: str,
        maneja_variantes: bool,
        producto_id=None,
        atributos_definicion: list[dict] | None = None,
    ) -> list[dict]:

        if not maneja_variantes:

            return []

        if not variantes:

            raise ValueError(
                "Agregue al menos una variante "
                "cuando el producto maneja variantes.",
            )

        claves_atributos = [
            item["clave"]
            for item in (
                atributos_definicion or []
            )
        ]

        existencia_existente: dict[
            str,
            float,
        ] = {}

        if producto_id is not None:

            for variante in cls.repositorio.listar_variantes(
                producto_id,
            ):

                existencia_existente[
                    str(
                        variante.codigo,
                    ).strip().upper()
                ] = float(
                    variante.existencia or 0,
                )

        codigos_vistos = set()
        barras_vistas = set()
        filas = []

        for indice, item in enumerate(
            variantes,
            start=1,
        ):

            talla = str(
                item.get(
                    "talla",
                    "",
                )
            ).strip()

            color = str(
                item.get(
                    "color",
                    "",
                )
            ).strip()

            calibre = str(
                item.get(
                    "calibre",
                    "",
                )
            ).strip()

            largo = str(
                item.get(
                    "largo",
                    "",
                )
            ).strip()

            atributos_raw = dict(
                item.get(
                    "atributos",
                )
                or {},
            )

            atributos = {}

            for clave in claves_atributos:

                valor = str(
                    atributos_raw.get(
                        clave,
                        "",
                    )
                    or "",
                ).strip()

                if valor:

                    atributos[clave] = valor

            tiene_dinamicos = bool(
                atributos,
            )

            if not any(
                (
                    talla,
                    color,
                    calibre,
                    largo,
                )
            ) and not tiene_dinamicos:

                raise ValueError(
                    f"La variante #{indice} debe indicar "
                    "talla, color, calibre, largo o algún "
                    "atributo adicional.",
                )

            codigo = str(
                item.get(
                    "codigo",
                    "",
                )
            ).strip().upper()

            if not codigo:

                codigo = (
                    f"{codigo_producto}-V"
                    f"{indice:02d}"
                )

            if codigo in codigos_vistos:

                raise ValueError(
                    f"El código de variante {codigo} "
                    "está repetido.",
                )

            if cls.repositorio.existe_codigo(
                codigo,
                producto_id,
            ):

                raise ValueError(
                    f"El código {codigo} ya está en uso "
                    "como producto base.",
                )

            if cls._codigo_variante_ocupado(
                codigo,
                producto_id,
            ):

                raise ValueError(
                    f"El código {codigo} ya está en uso "
                    "en otra variante.",
                )

            codigos_vistos.add(
                codigo,
            )

            codigo_barras = str(
                item.get(
                    "codigo_barras",
                    "",
                )
                or "",
            ).strip()

            if codigo_barras:

                if (
                    codigo_barras
                    in barras_vistas
                ):

                    raise ValueError(
                        "No repita el mismo código "
                        "de barras entre variantes.",
                    )

                if cls._codigo_barras_ocupado(
                    codigo_barras,
                    producto_id,
                ):

                    raise ValueError(
                        "Ya existe ese código de barras "
                        "en otro producto o variante.",
                    )

                barras_vistas.add(
                    codigo_barras,
                )

            precio_venta = item.get(
                "precio_venta",
            )

            if precio_venta is not None:

                precio_venta = float(
                    precio_venta,
                )

                if precio_venta <= 0:

                    precio_venta = None

            costo = item.get(
                "costo",
            )

            if costo is not None:

                costo = float(
                    costo,
                )

                if costo <= 0:

                    costo = None

            existencia = existencia_existente.get(
                codigo,
                0.0,
            )

            if existencia < 0:

                raise ValueError(
                    f"La existencia de la variante "
                    f"#{indice} no puede ser negativa.",
                )

            filas.append(
                {
                    "codigo": codigo,
                    "codigo_barras": (
                        codigo_barras
                        or None
                    ),
                    "talla": talla or None,
                    "color": color or None,
                    "calibre": calibre or None,
                    "largo": largo or None,
                    "atributos": atributos,
                    "precio_venta": precio_venta,
                    "costo": costo,
                    "existencia": existencia,
                    "precio_incluye_iva": None,
                    "impuesto_venta_id": None,
                    "impuesto_compra_id": None,
                    "imagen": None,
                    "activo": bool(
                        item.get(
                            "activo",
                            True,
                        )
                    ),
                },
            )

        return filas

    @classmethod
    def _codigo_variante_ocupado(
        cls,
        codigo: str,
        producto_id=None,
    ) -> bool:

        db = cls.repositorio.obtener_sesion()

        try:

            from .modelos import ProductoVariante

            consulta = (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.codigo == codigo,
                )
            )

            if producto_id is not None:

                consulta = consulta.filter(
                    ProductoVariante.producto_id
                    != producto_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def _codigo_barras_ocupado(
        cls,
        codigo_barras: str,
        producto_id=None,
    ) -> bool:

        if cls.repositorio.existe_codigo_barras(
            codigo_barras,
            producto_id,
        ):

            return True

        db = cls.repositorio.obtener_sesion()

        try:

            from .modelos import ProductoVariante

            consulta = (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.codigo_barras
                    == codigo_barras,
                )
            )

            if producto_id is not None:

                consulta = consulta.filter(
                    ProductoVariante.producto_id
                    != producto_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def _producto_a_lookup_result(
        cls,
        producto,
    ) -> LookupResult:

        return LookupResult(
            valor=producto.id,
            codigo=str(
                producto.codigo
                or "",
            ),
            texto=str(
                producto.nombre
                or "",
            ),
            objeto=producto,
        )

    @classmethod
    def _variante_a_lookup_result(
        cls,
        producto,
        variante,
    ) -> LookupResult:

        detalle = cls._etiqueta_variante(
            variante,
        )

        texto = str(
            producto.nombre
            or "",
        )

        if detalle:

            texto = (
                f"{texto} — {detalle}"
            )

        return LookupResult(
            valor=producto.id,
            codigo=str(
                variante.codigo
                or "",
            ),
            texto=texto,
            objeto=producto,
            producto_variante_id=variante.id,
        )

    @classmethod
    def buscar_para_lookup(
        cls,
        texto: str = "",
    ) -> list[LookupResult]:

        items: list[LookupResult] = []
        vistos = set()

        for variante, producto in cls.repositorio.buscar_variantes(
            texto,
        ):

            clave = (
                "v",
                variante.id,
            )

            if clave in vistos:

                continue

            vistos.add(
                clave,
            )

            items.append(
                cls._variante_a_lookup_result(
                    producto,
                    variante,
                ),
            )

        productos = cls.buscar(
            texto,
        )

        for producto in productos:

            if (
                not producto.activo
                or producto.maneja_variantes
            ):

                continue

            clave = (
                "p",
                producto.id,
            )

            if clave in vistos:

                continue

            vistos.add(
                clave,
            )

            items.append(
                cls._producto_a_lookup_result(
                    producto,
                ),
            )

        return items

    @classmethod
    def resolver_item(
        cls,
        producto_id,
        producto_variante_id=None,
    ) -> dict:

        producto = cls.obtener_por_id(
            producto_id,
        )

        if producto is None:

            raise ValueError(
                "No se encontró el producto.",
            )

        variante = None

        if producto_variante_id:

            variante = cls.repositorio.obtener_variante_por_id(
                producto_variante_id,
            )

            if (
                variante is None
                or variante.producto_id
                != producto.id
            ):

                raise ValueError(
                    "La variante no pertenece "
                    "al producto seleccionado.",
                )

        codigo = producto.codigo or ""

        nombre = producto.nombre or ""

        if variante is not None:

            codigo = variante.codigo or codigo

            detalle = cls._etiqueta_variante(
                variante,
            )

            if detalle:

                nombre = (
                    f"{nombre} — {detalle}"
                )

        precio_venta = float(
            producto.precio_venta
            or 0,
        )

        precio_incluye_iva = bool(
            producto.precio_incluye_iva,
        )

        impuesto_venta_id = producto.impuesto_venta_id

        imagen = producto.imagen

        if variante is not None:

            if (
                variante.precio_venta
                is not None
            ):

                precio_venta = float(
                    variante.precio_venta,
                )

            if (
                variante.precio_incluye_iva
                is not None
            ):

                precio_incluye_iva = bool(
                    variante.precio_incluye_iva,
                )

            if variante.impuesto_venta_id:

                impuesto_venta_id = (
                    variante.impuesto_venta_id
                )

            if variante.imagen:

                imagen = variante.imagen

        return {
            "producto_id": producto.id,
            "producto_variante_id": (
                variante.id
                if variante
                else None
            ),
            "codigo": codigo,
            "nombre": nombre,
            "precio_venta": precio_venta,
            "precio_incluye_iva": precio_incluye_iva,
            "impuesto_venta_id": impuesto_venta_id,
            "imagen": imagen,
            "producto": producto,
            "variante": variante,
        }

    @classmethod
    def obtener_variantes_formulario(
        cls,
        producto,
    ) -> list[dict]:

        filas = []

        definiciones = cls._definiciones_atributos_producto(
            producto,
        )

        for variante in cls.repositorio.listar_variantes(
            producto.id,
        ):

            filas.append(
                {
                    "codigo": variante.codigo,
                    "codigo_barras": (
                        variante.codigo_barras
                    ),
                    "talla": variante.talla,
                    "color": variante.color,
                    "calibre": variante.calibre,
                    "largo": variante.largo,
                    "atributos": dict(
                        variante.atributos or {},
                    ),
                    "precio_venta": (
                        variante.precio_venta
                    ),
                    "costo": variante.costo,
                    "existencia": float(
                        variante.existencia or 0,
                    ),
                    "activo": variante.activo,
                },
            )

        return filas, definiciones

    @classmethod
    def guardar_completo(
        cls,
        datos,
        id_registro=None,
    ):

        precios_raw = datos.pop(
            "_listas_precios",
            [],
        )

        variantes_raw = datos.pop(
            "_variantes",
            [],
        )

        atributos_variante = datos.pop(
            "_atributos_variante",
            [],
        )

        cls.validar(
            datos,
            id_registro,
        )

        precios = cls._validar_precios(
            precios_raw,
        )

        definiciones_atributos = [
            {
                "nombre": str(
                    item.get(
                        "nombre",
                        "",
                    )
                ).strip(),
                "clave": str(
                    item.get(
                        "clave",
                        "",
                    )
                ).strip(),
            }
            for item in (
                atributos_variante or []
            )
            if str(
                item.get(
                    "nombre",
                    "",
                )
            ).strip()
        ]

        datos["atributos_variante"] = (
            definiciones_atributos
        )

        variantes = cls._validar_variantes(
            variantes_raw,
            datos["codigo"],
            bool(
                datos.get(
                    "maneja_variantes",
                    False,
                )
            ),
            id_registro,
            definiciones_atributos,
        )

        precios = cls._sincronizar_precio_base(
            datos,
            precios,
        )

        lista = ServicioListaPrecio.obtener_predeterminada()

        if lista is not None:

            for item in precios:

                if item["lista_precio_id"] == lista.id:

                    datos["precio_venta"] = item[
                        "precio"
                    ]

                    break

        producto_datos = cls._filtrar_datos_producto(
            datos,
        )

        if id_registro is None:

            registro = cls.repositorio.guardar_completo(
                producto_datos,
                precios,
            )

        else:

            registro = cls.repositorio.actualizar_completo(
                id_registro,
                producto_datos,
                precios,
            )

        if registro is not None:

            cls.repositorio.guardar_variantes(
                registro.id,
                variantes,
            )

            if bool(
                registro.maneja_variantes,
            ):

                cls.repositorio.sincronizar_existencia_producto(
                    registro.id,
                )

            return cls.repositorio.obtener_completo(
                registro.id,
            )

        return registro

    @classmethod
    def obtener_completo(
        cls,
        id_registro,
    ):

        return cls.repositorio.obtener_completo(
            id_registro,
        )

    @classmethod
    def obtener_precios_formulario(
        cls,
        producto,
    ) -> list[dict]:

        from aplicacion.maestros.impuestos.repositorio import (
            RepositorioImpuesto,
        )
        from aplicacion.maestros.listas_precio.repositorio import (
            RepositorioListaPrecio,
        )

        filas = []

        for precio in producto.precios:

            lista = RepositorioListaPrecio.obtener_por_id(
                precio.lista_precio_id,
            )

            descripcion = ""

            if lista is not None:

                descripcion = (
                    f"{lista.codigo} - {lista.nombre}"
                )

            impuesto_texto = ""

            if precio.impuesto_id:

                impuesto = RepositorioImpuesto.obtener_por_id(
                    precio.impuesto_id,
                )

                if impuesto is not None:

                    from aplicacion.maestros.impuestos.etiquetas import (
                        etiqueta_impuesto,
                    )

                    impuesto_texto = etiqueta_impuesto(
                        impuesto,
                    )

            filas.append(
                {
                    "lista_precio_id": precio.lista_precio_id,
                    "descripcion": descripcion,
                    "precio": precio.precio,
                    "impuesto_id": precio.impuesto_id,
                    "impuesto_texto": impuesto_texto,
                },
            )

        return filas

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def ruta_imagen_por_codigo(
        cls,
        codigo: str | None,
    ) -> Path | None:

        codigo = str(
            codigo or "",
        ).strip()

        if not codigo:

            return None

        for extension in (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
        ):

            ruta = RUTA_IMAGENES / f"{codigo}{extension}"

            if ruta.is_file():

                return ruta

        return None

    @classmethod
    def ruta_imagen_absoluta(
        cls,
        ruta_relativa: str | None,
    ) -> Path | None:

        if not ruta_relativa:

            return None

        texto = str(
            ruta_relativa,
        ).strip().replace(
            "\\",
            "/",
        )

        if not texto:

            return None

        base = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "recursos"
            / "imagenes"
        )

        nombre = Path(
            texto,
        ).name

        candidatos = (
            Path(
                texto,
            ),
            Path(
                texto,
            ).expanduser(),
            base / texto,
            RUTA_IMAGENES / nombre,
            RUTA_IMAGENES / texto,
            base / "productos" / nombre,
        )

        vistos: set[str] = set()

        for ruta in candidatos:

            try:

                ruta_resuelta = ruta.resolve()

            except OSError:

                continue

            clave = str(
                ruta_resuelta,
            ).lower()

            if (
                clave in vistos
                or not ruta_resuelta.is_file()
            ):

                continue

            vistos.add(
                clave,
            )

            return ruta_resuelta

        return None

    @classmethod
    def resolver_imagen_producto(
        cls,
        producto,
    ) -> Path | None:

        if producto is None:

            return None

        ruta = cls.ruta_imagen_absoluta(
            getattr(
                producto,
                "imagen",
                None,
            ),
        )

        if ruta is not None:

            return ruta

        return cls.ruta_imagen_por_codigo(
            getattr(
                producto,
                "codigo",
                None,
            ),
        )

    @classmethod
    def resolver_imagen_item(
        cls,
        producto,
        variante=None,
    ) -> Path | None:

        if variante is not None:

            ruta = cls.ruta_imagen_absoluta(
                getattr(
                    variante,
                    "imagen",
                    None,
                ),
            )

            if ruta is not None:

                return ruta

        return cls.resolver_imagen_producto(
            producto,
        )

    @classmethod
    def cargar_pixmap_producto(
        cls,
        producto,
    ) -> QPixmap | None:

        from PySide6.QtGui import QPixmap

        ruta = cls.resolver_imagen_producto(
            producto,
        )

        if ruta is None:

            return None

        pixmap = QPixmap(
            str(
                ruta,
            ),
        )

        if pixmap.isNull():

            return None

        return pixmap

    @classmethod
    def inicializar_catalogos(cls):

        from aplicacion.maestros.impuestos.servicios import (
            ServicioImpuesto,
        )
        from aplicacion.maestros.unidades_medida.servicios import (
            ServicioUnidadMedida,
        )

        ServicioImpuesto.inicializar_predeterminados()
        ServicioListaPrecio.inicializar_predeterminados()
        ServicioUnidadMedida.inicializar_predeterminados()

        from aplicacion.maestros.productos.catalogo_variantes_servicio import (
            ServicioCatalogoVariantes,
        )

        ServicioCatalogoVariantes.asegurar_predeterminados()
