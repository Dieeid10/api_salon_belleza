from typing import Any

from psycopg import Connection, sql


class Crud:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def insert(self, table: str, data: dict[str, Any]) -> dict:
        query = sql.SQL("INSERT INTO {t} ({cols}) VALUES ({vals}) RETURNING *").format(
            t=sql.Identifier(table),
            cols=sql.SQL(", ").join(map(sql.Identifier, data)),
            vals=sql.SQL(", ").join(sql.Placeholder() * len(data)),
        )
        return self.conn.execute(query, tuple(data.values())).fetchone()

    def select(self, table: str, id_value: Any, id_field: str = "id") -> dict | None:
        query = sql.SQL("SELECT * FROM {t} WHERE {f} = %s").format(
            t=sql.Identifier(table), f=sql.Identifier(id_field)
        )
        return self.conn.execute(query, (id_value,)).fetchone()

    def select_all(
        self, table: str, condition: str | None = None, parameters: tuple = ()
    ) -> list[dict]:
        # `condition` debe ser texto escrito por vos en el código, nunca input del usuario.
        # Los valores siempre van en `parameters`, con %s.
        query = sql.SQL("SELECT * FROM {t}").format(t=sql.Identifier(table))
        if condition:
            query += sql.SQL(" WHERE ") + sql.SQL(condition)
        return self.conn.execute(query, parameters).fetchall()

    def update(
        self, table: str, id_value: Any, data: dict[str, Any], id_field: str = "id"
    ) -> dict | None:
        sets = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col)) for col in data
        )
        query = sql.SQL("UPDATE {t} SET {sets} WHERE {f} = %s RETURNING *").format(
            t=sql.Identifier(table), sets=sets, f=sql.Identifier(id_field)
        )
        return self.conn.execute(query, (*data.values(), id_value)).fetchone()

    def delete(self, table: str, id_value: Any, id_field: str = "id") -> bool:
        query = sql.SQL("DELETE FROM {t} WHERE {f} = %s").format(
            t=sql.Identifier(table), f=sql.Identifier(id_field)
        )
        return self.conn.execute(query, (id_value,)).rowcount > 0