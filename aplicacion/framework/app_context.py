class AppContext:
    """
    Contexto global de la aplicación.

    Permite compartir objetos importantes entre
    todos los módulos del ERP sin acoplar clases.
    """

    usuario = None

    empresa = None

    area_trabajo = None

    dashboard = None

    barra_estado = None

    navegacion = None

    sesion = None

    configuracion = {}
