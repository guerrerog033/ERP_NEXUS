from __future__ import annotations

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)


EmpresaTable = TableDefinition(

    titulo="Empresas",

    columnas=[

        Column(
            nombre="id",
            etiqueta="ID",
            visible=False,
        ),

        Column(
            nombre="nit",
            etiqueta="NIT",
        ),

        Column(
            nombre="dv",
            etiqueta="DV",
        ),

        Column(
            nombre="razon_social",
            etiqueta="Razón Social",
        ),

        Column(
            nombre="nombre_comercial",
            etiqueta="Nombre Comercial",
        ),

        Column(
            nombre="representante_legal",
            etiqueta="Representante Legal",
        ),

        Column(
            nombre="actividad_economica",
            etiqueta="Actividad Económica",
        ),

        Column(
            nombre="regimen_tributario",
            etiqueta="Régimen Tributario",
        ),

        Column(
            nombre="responsable_iva",
            etiqueta="Resp. IVA",
        ),

        Column(
            nombre="direccion",
            etiqueta="Dirección",
        ),

        Column(
            nombre="pais",
            etiqueta="País",
        ),

        Column(
            nombre="departamento",
            etiqueta="Departamento",
        ),

        Column(
            nombre="ciudad",
            etiqueta="Ciudad",
        ),

        Column(
            nombre="telefono",
            etiqueta="Teléfono",
        ),

        Column(
            nombre="celular",
            etiqueta="Celular",
        ),

        Column(
            nombre="correo",
            etiqueta="Correo",
        ),

        Column(
            nombre="sitio_web",
            etiqueta="Sitio Web",
        ),

        Column(
            nombre="activo",
            etiqueta="Activa",
        ),

    ],

)
