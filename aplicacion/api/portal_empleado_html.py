from __future__ import annotations

_ESTILOS = """
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, Arial, sans-serif;
    margin: 0;
    padding: 16px;
    background: #f4f6f8;
    color: #1f2937;
  }
  h1 { font-size: 1.3rem; margin: 0 0 4px; }
  h2 { font-size: 1.05rem; margin: 20px 0 8px; }
  .barra {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .barra a { color: #1B4F8A; font-size: 0.85rem; }
  .tarjeta {
    background: #fff;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  .menu a {
    display: block;
    background: #fff;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 10px;
    text-decoration: none;
    color: #1B4F8A;
    font-weight: 600;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  .cifra { font-size: 1.4rem; font-weight: 700; }
  .cifra.rojo { color: #b91c1c; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  th, td { text-align: left; padding: 6px 4px; border-bottom: 1px solid #e5e7eb; }
  th { color: #6b7280; font-weight: 600; }
  input[type=text], input[type=password] {
    width: 100%;
    padding: 12px;
    font-size: 1rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    margin-bottom: 12px;
  }
  button, .boton {
    width: 100%;
    padding: 12px;
    font-size: 1rem;
    background: #1B4F8A;
    color: #fff;
    border: none;
    border-radius: 8px;
  }
  .error { color: #b91c1c; margin-bottom: 12px; }
</style>
"""


def _envolver(
    titulo: str,
    cuerpo: str,
) -> str:

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
{_ESTILOS}
</head>
<body>
{cuerpo}
</body>
</html>"""


def pagina_login(
    error: str = "",
) -> str:

    mensaje_error = (
        f'<p class="error">{error}</p>' if error else ""
    )

    return _envolver(
        "ERP NEXUS — Acceso",
        f"""
        <h1>ERP NEXUS</h1>
        <p>Portal móvil de empleados</p>
        {mensaje_error}
        <form method="post" action="/portal/empleado/login">
          <label>Usuario</label>
          <input type="text" name="usuario" required autofocus>
          <label>Contraseña</label>
          <input type="password" name="password" required>
          <button type="submit">Ingresar</button>
        </form>
        """,
    )


def _barra(
    nombre: str,
    token: str,
    *,
    mostrar_volver: bool = True,
) -> str:

    volver = (
        f'<a href="/portal/empleado/panel?token={token}">'
        "‹ Panel</a>"
        if mostrar_volver
        else "<span></span>"
    )

    return f"""
    <div class="barra">
        {volver}
        <a href="/portal/empleado/salir?token={token}">
            {nombre} · Salir
        </a>
    </div>
    """


def pagina_panel(
    nombre: str,
    token: str,
) -> str:

    return _envolver(
        "ERP NEXUS — Panel",
        f"""
        {_barra(nombre, token, mostrar_volver=False)}
        <h1>Hola, {nombre}</h1>
        <div class="menu">
            <a href="/portal/empleado/cartera?token={token}">
                💰 Cartera
            </a>
            <a href="/portal/empleado/ventas?token={token}">
                🧾 Ventas del día
            </a>
            <a href="/portal/empleado/inventario?token={token}">
                📦 Inventario
            </a>
        </div>
        """,
    )


def pagina_cartera(
    nombre: str,
    token: str,
    resumen: dict,
) -> str:

    filas = "".join(
        f"""
        <tr>
            <td>{fila['tercero']}</td>
            <td style="text-align:right;">
                ${fila['saldo']:,.0f}
            </td>
            <td style="text-align:right;">
                {fila['dias_mora']}d
            </td>
        </tr>
        """
        for fila in resumen.get(
            "clientes_vencidos",
            [],
        )
    )

    tabla = (
        f"""
        <h2>Mayor cartera vencida</h2>
        <table>
            <thead><tr>
                <th>Cliente</th><th>Saldo</th><th>Mora</th>
            </tr></thead>
            <tbody>{filas}</tbody>
        </table>
        """
        if filas
        else "<p>No hay cartera vencida. 🎉</p>"
    )

    return _envolver(
        "ERP NEXUS — Cartera",
        f"""
        {_barra(nombre, token)}
        <h1>Cartera</h1>
        <div class="tarjeta">
            <div>Por cobrar (total)</div>
            <div class="cifra">
                ${resumen['cxc_total']:,.0f}
            </div>
        </div>
        <div class="tarjeta">
            <div>Por cobrar (vencida)</div>
            <div class="cifra rojo">
                ${resumen['cxc_vencido']:,.0f}
            </div>
        </div>
        {tabla}
        """,
    )


def pagina_ventas(
    nombre: str,
    token: str,
    datos: dict,
) -> str:

    filas = "".join(
        f"""
        <tr>
            <td>{fila['numero']}</td>
            <td>{fila['cliente']}</td>
            <td style="text-align:right;">
                ${fila.get('total', 0):,.0f}
            </td>
        </tr>
        """
        for fila in datos.get(
            "facturas",
            [],
        )
    )

    tabla = (
        f"""
        <table>
            <thead><tr>
                <th>Número</th><th>Cliente</th><th>Total</th>
            </tr></thead>
            <tbody>{filas}</tbody>
        </table>
        """
        if filas
        else "<p>Sin facturas hoy todavía.</p>"
    )

    return _envolver(
        "ERP NEXUS — Ventas del día",
        f"""
        {_barra(nombre, token)}
        <h1>Ventas de hoy</h1>
        <div class="tarjeta">
            <div>Total facturado ({datos['cantidad']})</div>
            <div class="cifra">${datos['total']:,.0f}</div>
        </div>
        <h2>Facturas de hoy</h2>
        {tabla}
        """,
    )


def pagina_inventario(
    nombre: str,
    token: str,
    texto: str,
    resultados: list[dict],
) -> str:

    filas = "".join(
        f"""
        <tr>
            <td>{producto['codigo']}<br>
                <span style="color:#6b7280;">
                    {producto['nombre']}
                </span>
            </td>
            <td style="text-align:right;">
                {producto['existencia']:,.0f}
            </td>
        </tr>
        """
        for producto in resultados
    )

    if texto and not resultados:

        tabla = "<p>No se encontraron productos.</p>"

    elif resultados:

        tabla = f"""
        <table>
            <thead><tr>
                <th>Producto</th><th>Existencia</th>
            </tr></thead>
            <tbody>{filas}</tbody>
        </table>
        """

    else:

        tabla = ""

    return _envolver(
        "ERP NEXUS — Inventario",
        f"""
        {_barra(nombre, token)}
        <h1>Inventario</h1>
        <form method="get"
              action="/portal/empleado/inventario">
          <input type="hidden" name="token" value="{token}">
          <input type="text" name="q" value="{texto}"
                 placeholder="Buscar por código o nombre"
                 autofocus>
          <button type="submit">Buscar</button>
        </form>
        {tabla}
        """,
    )
