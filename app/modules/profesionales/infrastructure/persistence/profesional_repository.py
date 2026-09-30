from psycopg import Connection

from app.modules.profesionales.domain.entities import Profesional
from app.shared.infrastructure.db.crud import Crud

TABLE = "profesionales"

class PsycopgProfesionalRepository:
    def __init__(self, conn: Connection) -> None:
        self._crud = Crud(conn)

    def crear(self, profesional: Profesional) -> Profesional:
        row = self._crud.insert(TABLE, {
            "nombre": profesional.nombre,
            "perfil_id": profesional.perfil_id,
            "activo": profesional.activo,
        })
        return self._to_entity(row)

    def obtener(self, profesional_id: int) -> Profesional | None:
        row = self._crud.select(TABLE, profesional_id)
        return self._to_entity(row) if row else None

    def listar(self, solo_activos: bool = True) -> list[Profesional]:
        if solo_activos:
            rows = self._crud.select_all(TABLE, "activo = %s", (True,))
        else:
            rows = self._crud.select_all(TABLE)
        return [self._to_entity(r) for r in rows]

    def esta_activo(self, profesional_id: int) -> bool:
        row = self._crud.conn.execute(
            "SELECT 1 FROM profesionales WHERE id = %s AND activo",
            (profesional_id,),
        ).fetchone()
        return row is not None

    def actualizar(self, profesional: Profesional) -> Profesional:
        row = self._crud.update(TABLE, profesional.id, {
            "nombre": profesional.nombre,
            "perfil_id": profesional.perfil_id,
            "activo": profesional.activo,
        })
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: dict) -> Profesional:
        return Profesional(
            id=row["id"],
            nombre=row["nombre"],
            perfil_id=str(row["perfil_id"]) if row["perfil_id"] is not None else None,
            activo=row["activo"],
        )