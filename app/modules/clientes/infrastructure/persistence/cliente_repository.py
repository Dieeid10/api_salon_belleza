from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.modules.clientes.domain.entities import Cliente
from app.shared.error import ConflictError
from app.shared.infrastructure.db.crud import Crud

TABLE = "clientes"

class PsycopgClienteRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn
        self._crud = Crud(conn)

    def crear(self, cliente: Cliente) -> Cliente:
        try:
            row = self._crud.insert(TABLE, self._to_data(cliente, incluir_activo=False))
        except UniqueViolation as error:
            self._raise_email_conflict(error)
        return self._to_entity(row)

    def obtener(self, cliente_id: int) -> Cliente | None:
        row = self._crud.select(TABLE, cliente_id)
        return self._to_entity(row) if row else None

    def listar(self, solo_activos: bool = True) -> list[Cliente]:
        if solo_activos:
            rows = self._crud.select_all(TABLE, "activo = %s", (True,))
        else:
            rows = self._crud.select_all(TABLE)
        return [self._to_entity(row) for row in sorted(rows, key=lambda row: row["id"])]

    def obtener_o_crear_para_reserva(
        self, nombre: str, apellido: str, telefono: str
    ) -> int:
        nombre = nombre.strip()
        apellido = apellido.strip()
        telefono = telefono.strip()

        # Serializa reservas simultáneas con el mismo teléfono, aunque no haya fila.
        self._conn.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (telefono,),
        )
        row = self._conn.execute(
            "SELECT id FROM clientes WHERE telefono = %s ORDER BY activo DESC, id LIMIT 1 FOR UPDATE",
            (telefono,),
        ).fetchone()
        if row:
            self._conn.execute(
                "UPDATE clientes SET nombre = %s, apellido = %s, activo = true WHERE id = %s",
                (nombre, apellido, row["id"]),
            )
            return row["id"]

        row = self._crud.insert(
            TABLE,
            {
                "nombre": nombre,
                "apellido": apellido,
                "telefono": telefono,
            },
        )
        return row["id"]

    def actualizar(self, cliente: Cliente) -> Cliente:
        if cliente.id is None:
            raise ValueError("No se puede actualizar una clienta sin id")
        try:
            row = self._crud.update(TABLE, cliente.id, self._to_data(cliente))
        except UniqueViolation as error:
            self._raise_email_conflict(error)
        if row is None:
            raise ValueError("La clienta dejó de existir durante la actualización")
        return self._to_entity(row)

    @staticmethod
    def _to_data(cliente: Cliente, incluir_activo: bool = True) -> dict:
        data = {
            "nombre": cliente.nombre,
            "apellido": cliente.apellido,
            "telefono": cliente.telefono,
            "email": cliente.email,
        }
        if incluir_activo:
            data["activo"] = cliente.activo
        return data

    @staticmethod
    def _to_entity(row: dict) -> Cliente:
        return Cliente(
            id=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            telefono=row["telefono"],
            email=row["email"],
            activo=row["activo"],
            fecha_creacion=row["fecha_creacion"],
        )

    @staticmethod
    def _raise_email_conflict(error: UniqueViolation) -> None:
        if error.diag.constraint_name == "uq_clientes_email":
            raise ConflictError("Ya existe una clienta con ese email") from error
        raise error