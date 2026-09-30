from datetime import date

from psycopg import Connection

from app.modules.profesionales.application.dto import HorarioAtencionInfo


class PsycopgHorarioAtencionRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def jornada(
        self, profesional_id: int, fecha: date
    ) -> list[HorarioAtencionInfo]:
        dia_semana = (fecha.weekday() + 1) % 7
        rows = self._conn.execute(
            """
            SELECT hora_apertura, hora_cierre
            FROM horarios_atencion
            WHERE profesional_id = %s AND dia_semana = %s AND activo
            ORDER BY hora_apertura
            """,
            (profesional_id, dia_semana),
        ).fetchall()
        return [
            HorarioAtencionInfo(
                hora_apertura=row["hora_apertura"],
                hora_cierre=row["hora_cierre"],
            )
            for row in rows
        ]