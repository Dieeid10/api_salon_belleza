from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.modules.clientes.domain.entities import Client
from app.shared.error import ConflictError
from app.shared.infrastructure.db.crud import Crud

TABLE = "clientes"

class PsycopgClientRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn
        self._crud = Crud(conn)

    def create(self, client: Client) -> Client:
        try:
            row = self._crud.insert(
                TABLE,
                self._to_database_record(client, include_active=False),
            )
        except UniqueViolation as error:
            self._raise_email_conflict(error)
        return self._to_client(row)

    def get(self, client_id: int) -> Client | None:
        row = self._crud.select(TABLE, client_id)
        return self._to_client(row) if row else None

    def list_all(self, active_only: bool = True) -> list[Client]:
        if active_only:
            rows = self._crud.select_all(TABLE, "activo = %s", (True,))
        else:
            rows = self._crud.select_all(TABLE)
        return [
            self._to_client(row)
            for row in sorted(rows, key=lambda row: row["id"])
        ]

    def get_or_create_for_reservation(
        self, first_name: str, last_name: str, phone: str
    ) -> int:
        first_name = first_name.strip()
        last_name = last_name.strip()
        phone = phone.strip()

        # Serializa reservas simultáneas con el mismo teléfono, aunque no haya fila.
        self._conn.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (phone,),
        )
        row = self._conn.execute(
            "SELECT id FROM clientes WHERE telefono = %s ORDER BY activo DESC, id LIMIT 1 FOR UPDATE",
            (phone,),
        ).fetchone()
        if row:
            self._conn.execute(
                "UPDATE clientes SET nombre = %s, apellido = %s, activo = true WHERE id = %s",
                (first_name, last_name, row["id"]),
            )
            return row["id"]

        row = self._crud.insert(
            TABLE,
            {
                "nombre": first_name,
                "apellido": last_name,
                "telefono": phone,
            },
        )
        return row["id"]

    def update(self, client: Client) -> Client:
        if client.id is None:
            raise ValueError("No se puede actualizar una clienta sin id")
        try:
            row = self._crud.update(
                TABLE,
                client.id,
                self._to_database_record(client),
            )
        except UniqueViolation as error:
            self._raise_email_conflict(error)
        if row is None:
            raise ValueError("La clienta dejó de existir durante la actualización")
        return self._to_client(row)

    @staticmethod
    def _to_database_record(client: Client, include_active: bool = True) -> dict:
        data = {
            "nombre": client.first_name,
            "apellido": client.last_name,
            "telefono": client.phone,
            "email": client.email,
        }
        if include_active:
            data["activo"] = client.is_active
        return data

    @staticmethod
    def _to_client(row: dict) -> Client:
        return Client(
            id=row["id"],
            first_name=row["nombre"],
            last_name=row["apellido"],
            phone=row["telefono"],
            email=row["email"],
            is_active=row["activo"],
            created_at=row["fecha_creacion"],
        )

    @staticmethod
    def _raise_email_conflict(error: UniqueViolation) -> None:
        if error.diag.constraint_name == "uq_clientes_email":
            raise ConflictError("Ya existe una clienta con ese email") from error
        raise error