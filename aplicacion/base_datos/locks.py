from aplicacion.base_datos.admin import conexion_admin


def liberar_locks_terceros() -> int:

    terminados = 0

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute(
            """
            SELECT DISTINCT a.pid, a.state, left(a.query, 120)
            FROM pg_stat_activity a
            LEFT JOIN pg_locks l ON l.pid = a.pid
            LEFT JOIN pg_class c ON c.oid = l.relation
            WHERE a.datname = current_database()
              AND a.pid <> pg_backend_pid()
              AND (
                  a.state = 'idle in transaction'
                  OR a.query ILIKE '%ALTER TABLE terceros%'
                  OR (
                      c.relname = 'terceros'
                      AND a.wait_event_type = 'Lock'
                  )
              )
            """
        )

        for pid, state, query in cur.fetchall():

            print(
                "Liberando sesión bloqueada: "
                f"pid={pid} state={state} "
                f"query={query!r}"
            )

            cur.execute(
                "SELECT pg_terminate_backend(%s)",
                (pid,),
            )

            terminados += 1

        cur.close()

    finally:

        conexion.close()

    if terminados:

        print(
            f"Sesiones terminadas en terceros: "
            f"{terminados}"
        )

    return terminados
