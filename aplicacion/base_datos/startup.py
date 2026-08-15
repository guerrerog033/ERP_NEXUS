from aplicacion.base_datos.conexion import (

    Base,

    engine,

)



_inicializado = False

_migraciones_aplicadas = False





def inicializar_sistema() -> None:

    global _inicializado

    if _inicializado:

        return

    from aplicacion.nucleo.log import (
        configurar_logging,
    )

    configurar_logging()

    from aplicacion.maestros.terceros.registro import (

        registrar as registrar_documentos,

    )



    registrar_documentos()



    from aplicacion.base_datos.registro_modelos import (

        importar_modelos,

    )



    importar_modelos()



    Base.metadata.create_all(

        bind=engine,

    )



    _inicializado = True





def aplicar_migraciones() -> None:



    global _migraciones_aplicadas



    if _migraciones_aplicadas:



        return



    from aplicacion.base_datos.alembic_bridge import (

        aplicar_esquema,

    )



    aplicar_esquema()



    from aplicacion.maestros.productos.servicios import (

        ServicioProducto,

    )



    ServicioProducto.inicializar_catalogos()



    _migraciones_aplicadas = True

