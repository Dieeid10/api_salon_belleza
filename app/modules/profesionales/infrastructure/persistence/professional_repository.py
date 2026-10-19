from psycopg import Connection

from app.modules.profesionales.domain.entities import Professional
from app.shared.infrastructure.db.crud import Crud

TABLE = "profesionales"

class PsycopgProfessionalRepository:
    def __init__(self, conn: Connection) -> None:
        self._crud = Crud(conn)

    def create(self, profesional: Professional) -> Professional:
        row = self._crud.insert(TABLE, {
            "nombre": profesional.nombre,
            "perfil_id": profesional.perfil_id,
            "activo": profesional.activo,
        })
        return self._to_professional(row)

    def get(self, profesional_id: int) -> Professional | None:
        row = self._crud.select(TABLE, profesional_id)
        return self._to_professional(row) if row else None

    def list_all(self, solo_activos: bool = True) -> list[Professional]:
        if solo_activos:
            rows = self._crud.select_all(TABLE, "activo = %s", (True,))
        else:
            rows = self._crud.select_all(TABLE)
        return [self._to_professional(r) for r in rows]

    def is_active(self, profesional_id: int) -> bool:
        row = self._crud.conn.execute(
            "SELECT 1 FROM profesionales WHERE id = %s AND activo",
            (profesional_id,),
        ).fetchone()
        return row is not None

    def update(self, profesional: Professional) -> Professional:
        row = self._crud.update(TABLE, profesional.id, {
            "nombre": profesional.nombre,
            "perfil_id": profesional.perfil_id,
            "activo": profesional.activo,
        })
        return self._to_professional(row)

    @staticmethod
    def _to_professional(row: dict) -> Professional:
        return Professional(
            id=row["id"],
            nombre=row["nombre"],
            perfil_id=str(row["perfil_id"]) if row["perfil_id"] is not None else None,
            activo=row["activo"],
        )