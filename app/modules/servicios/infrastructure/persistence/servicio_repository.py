from decimal import Decimal

from psycopg import Connection

from app.modules.servicios.application.dto import ServicioCatalogoInfo
from app.modules.servicios.domain.entities import Servicio
from app.shared.infrastructure.db.crud import Crud

TABLE = "servicios"


class PsycopgServicioRepository:
    def __init__(self, conn: Connection) -> None:
        self._crud = Crud(conn)

    def crear(self, servicio: Servicio) -> Servicio:
        row = self._crud.insert(TABLE, self._to_data(servicio))
        return self._to_entity(row)

    def obtener(self, servicio_id: int) -> Servicio | None:
        row = self._crud.select(TABLE, servicio_id)
        return self._to_entity(row) if row else None

    def obtener_activos(self, servicio_ids: list[int]) -> list[ServicioCatalogoInfo]:
        if not servicio_ids:
            return []
        rows = self._crud.conn.execute(
            """
            SELECT id, nombre_servicio, duracion_minutos, precio
            FROM servicios
            WHERE id = ANY(%s) AND activo
            ORDER BY id
            """,
            (servicio_ids,),
        ).fetchall()
        return [
            ServicioCatalogoInfo(
                id=row["id"],
                nombre=row["nombre_servicio"],
                duracion_min=row["duracion_minutos"],
                precio=Decimal(row["precio"]),
            )
            for row in rows
        ]

    def listar(
        self, solo_activos: bool = True, solo_visibles_online: bool = True
    ) -> list[Servicio]:
        condiciones: list[str] = []
        parametros: list[bool] = []
        if solo_activos:
            condiciones.append("activo = %s")
            parametros.append(True)
        if solo_visibles_online:
            condiciones.append("visible_online = %s")
            parametros.append(True)

        rows = self._crud.select_all(
            TABLE,
            " AND ".join(condiciones) if condiciones else None,
            tuple(parametros),
        )
        return [self._to_entity(row) for row in rows]

    def actualizar(self, servicio: Servicio) -> Servicio:
        if servicio.id is None:
            raise ValueError("No se puede actualizar un servicio sin id")
        row = self._crud.update(TABLE, servicio.id, self._to_data(servicio))
        if row is None:
            raise ValueError("El servicio dejó de existir durante la actualización")
        return self._to_entity(row)

    @staticmethod
    def _to_data(servicio: Servicio) -> dict:
        return {
            "nombre_servicio": servicio.nombre_servicio,
            "descripcion": servicio.descripcion,
            "precio": servicio.precio,
            "duracion_minutos": servicio.duracion_minutos,
            "visible_online": servicio.visible_online,
            "activo": servicio.activo,
        }

    @staticmethod
    def _to_entity(row: dict) -> Servicio:
        return Servicio(
            id=row["id"],
            nombre_servicio=row["nombre_servicio"],
            descripcion=row["descripcion"],
            precio=Decimal(row["precio"]),
            duracion_minutos=row["duracion_minutos"],
            visible_online=row["visible_online"],
            activo=row["activo"],
        )