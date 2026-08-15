from aplicacion.maestros.marcas.marca_lookup import MarcaLookup

lookup = MarcaLookup()

resultados = lookup.buscar()

print(type(resultados))

for r in resultados:

    print(
        r.valor,
        r.codigo,
        r.texto,
    )