from datetime import datetime
from decimal import Decimal

from psycopg import Connection
from psycopg.errors import ExclusionViolation

from app.modules.turnos.domain.entities import DetalleTurno, Turno
from app.modules.turnos.application.dto import DetalleTurnoVentaInfo, TurnoVentaInfo
from app.modules.turnos.domain.errors import HorarioNoDisponible
from app.modules.turnos.domain.value_objects import (
    ESTADOS_ACTIVOS, EstadoTurno, FranjaHoraria,
)
from app.shared.infrastructure.db.crud import Crud


ESTADO_A_DB = {
    EstadoTurno.PENDIENTE: "Pendiente",
    EstadoTurno.CONFIRMADO: "Confirmado",
    EstadoTurno.COMPLETADO: "Realizado",
    EstadoTurno.CANCELADO: "Cancelado",
    EstadoTurno.AUSENTE: "Ausente",
}
DB_A_ESTADO = {valor: estado for estado, valor in ESTADO_A_DB.items()}


class PsycopgTurnoRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn
        self._crud = Crud(conn)

    def crear(self, turno: Turno) -> Turno:
        try:
            row = self._crud.insert("turnos", {
                "cliente_id": turno.cliente_id,
                "profesional_id": turno.profesional_id,
                "fecha_hora": turno.franja.inicio,
                "fecha_hora_fin": turno.franja.fin,
                "estado": ESTADO_A_DB[turno.estado],
            })
        except ExclusionViolation:
            raise HorarioNoDisponible()

        for d in turno.detalles:
            self._crud.insert("detalle_turnos", {
                "turno_id": row["id"],
                "servicio_id": d.servicio_id,
                "precio_lista": d.precio,
                "descuento_pct": Decimal("0"),
                "precio_reservado": d.precio,
            })
        turno.id = row["id"]
        return turno

    def obtener(self, turno_id: int, bloquear: bool = False) -> Turno | None:
        # FOR UPDATE evita que dos cambios de estado simultáneos se pisen
        lock = " FOR UPDATE" if bloquear else ""
        row = self._conn.execute(
            f"SELECT * FROM turnos WHERE id = %s{lock}", (turno_id,)
        ).fetchone()
        if row is None:
            return None
        return self._to_entity(row, self._detalles([turno_id]).get(turno_id, []))

    def obtener_para_venta(self, turno_id: int, bloquear: bool = False) -> TurnoVentaInfo | None:
        lock = " FOR UPDATE" if bloquear else ""
        row = self._conn.execute(
            f"SELECT id, cliente_id, estado FROM turnos WHERE id = %s{lock}",
            (turno_id,),
        ).fetchone()
        if row is None:
            return None
        rows = self._conn.execute(
            """
            SELECT servicio_id, descuento_id, precio_lista, descuento_pct,
                   precio_reservado
                 FROM detalle_turnos
            WHERE turno_id = %s
            ORDER BY id
            """,
            (turno_id,),
        ).fetchall()
        detalles = [
            DetalleTurnoVentaInfo(
                servicio_id=detalle["servicio_id"],
                descuento_id=detalle["descuento_id"],
                precio_lista=Decimal(detalle["precio_lista"]),
                descuento_pct=Decimal(detalle["descuento_pct"]),
                precio_reservado=Decimal(detalle["precio_reservado"]),
            )
            for detalle in rows
        ]
        return TurnoVentaInfo(
            id=row["id"],
            cliente_id=row["cliente_id"],
            estado=row["estado"],
            detalles=detalles,
        )

    def actualizar_estado(self, turno: Turno) -> None:
        self._crud.update("turnos", turno.id, {"estado": ESTADO_A_DB[turno.estado]})

    def listar_ocupados(self, profesional_id: int, desde: datetime, hasta: datetime) -> list[FranjaHoraria]:
        rows = self._conn.execute(
            """
                SELECT fecha_hora AS inicio, fecha_hora_fin AS fin FROM turnos
                WHERE profesional_id = %s
                AND estado = ANY(%s)
                AND fecha_hora < %s AND fecha_hora_fin > %s
            """,
            (profesional_id, [ESTADO_A_DB[estado] for estado in ESTADOS_ACTIVOS], hasta, desde),
        ).fetchall()
        return [FranjaHoraria(r["inicio"], r["fin"]) for r in rows]

    def listar(self, desde: datetime, hasta: datetime, profesional_id: int | None = None, estado: EstadoTurno | None = None) -> list[Turno]:
        # Las condiciones son literales del código; los valores van siempre como parámetros
        where = ["fecha_hora >= %s", "fecha_hora < %s"]
        params: list = [desde, hasta]
        if profesional_id is not None:
            where.append("profesional_id = %s")
            params.append(profesional_id)
        if estado is not None:
            where.append("estado = %s")
            params.append(ESTADO_A_DB[estado])

        rows = self._conn.execute(
            f"SELECT * FROM turnos WHERE {' AND '.join(where)} ORDER BY fecha_hora", params
        ).fetchall()
        detalles = self._detalles([r["id"] for r in rows])  # una sola consulta, sin N+1
        return [self._to_entity(r, detalles.get(r["id"], [])) for r in rows]

    def _detalles(self, turno_ids: list[int]) -> dict[int, list[DetalleTurno]]:
        if not turno_ids:
            return {}
        rows = self._conn.execute(
            """
            SELECT d.turno_id, d.servicio_id,
                   s.nombre_servicio AS nombre,
                   s.duracion_minutos AS duracion_min,
                   d.precio_reservado AS precio
            FROM detalle_turnos d
            JOIN servicios s ON s.id = d.servicio_id
            WHERE d.turno_id = ANY(%s)
            ORDER BY d.turno_id, d.servicio_id
            """,
            (turno_ids,),
        ).fetchall()
        resultado: dict[int, list[DetalleTurno]] = {}
        for r in rows:
            resultado.setdefault(r["turno_id"], []).append(
                DetalleTurno(
                    r["servicio_id"],
                    r["nombre"],
                    r["duracion_min"],
                    Decimal(r["precio"]),
                )
            )
        return resultado

    @staticmethod
    def _to_entity(row: dict, detalles: list[DetalleTurno]) -> Turno:
        return Turno(
            id=row["id"],
            cliente_id=row["cliente_id"],
            profesional_id=row["profesional_id"],
            franja=FranjaHoraria(
                row["inicio"] if "inicio" in row else row["fecha_hora"],
                row["fin"] if "fin" in row else row["fecha_hora_fin"],
            ),
            estado=DB_A_ESTADO[row["estado"]],
            detalles=detalles,
        )