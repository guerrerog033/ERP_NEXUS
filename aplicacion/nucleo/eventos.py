class Eventos:

    _eventos = {}

    @classmethod
    def suscribir(cls, nombre_evento, funcion):

        if nombre_evento not in cls._eventos:
            cls._eventos[nombre_evento] = []

        if funcion not in cls._eventos[nombre_evento]:
            cls._eventos[nombre_evento].append(funcion)

    @classmethod
    def cancelar(cls, nombre_evento, funcion):

        if nombre_evento in cls._eventos:

            if funcion in cls._eventos[nombre_evento]:
                cls._eventos[nombre_evento].remove(funcion)

    @classmethod
    def emitir(cls, nombre_evento, *args, **kwargs):

        if nombre_evento not in cls._eventos:
            return

        for funcion in cls._eventos[nombre_evento]:
            funcion(*args, **kwargs)

    @classmethod
    def limpiar(cls):

        cls._eventos.clear()