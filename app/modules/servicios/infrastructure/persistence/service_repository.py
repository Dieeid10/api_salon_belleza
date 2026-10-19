from decimal import Decimal

from psycopg import Connection

from app.modules.servicios.application.dto import ServiceCatalogInfo
from app.modules.servicios.domain.entities import Service
from app.shared.infrastructure.db.crud import Crud

TABLE = "servicios"


class PsycopgServiceRepository:
    def __init__(self, conn: Connection) -> None:
        self._crud = Crud(conn)

    def create(self, servicio: Service) -> Service:
        row = self._crud.insert(TABLE, self._to_database_record(servicio))
        return self._to_service(row)

    def get(self, servicio_id: int) -> Service | None:
        row = self._crud.select(TABLE, servicio_id)
        return self._to_service(row) if row else None

    def get_active(self, servicio_ids: list[int]) -> list[ServiceCatalogInfo]:
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
            ServiceCatalogInfo(
                id=row["id"],
                nombre=row["nombre_servicio"],
                duracion_min=row["duracion_minutos"],
                precio=Decimal(row["precio"]),
            )
            for row in rows
        ]

    def list_all(
        self, active_only: bool = True, online_only: bool = True
    ) -> list[Service]:
        condiciones: list[str] = []
        parametros: list[bool] = []
        if active_only:
            condiciones.append("activo = %s")
            parametros.append(True)
        if online_only:
            condiciones.append("visible_online = %s")
            parametros.append(True)

        rows = self._crud.select_all(
            TABLE,
            " AND ".join(condiciones) if condiciones else None,
            tuple(parametros),
        )
        return [self._to_service(row) for row in rows]

    def update(self, servicio: Service) -> Service:
        if servicio.id is None:
            raise ValueError("No se puede actualizar un servicio sin id")
        row = self._crud.update(TABLE, servicio.id, self._to_database_record(servicio))
        if row is None:
            raise ValueError("El servicio dejó de existir durante la actualización")
        return self._to_service(row)

    @staticmethod
    def _to_database_record(servicio: Service) -> dict:
        return {
            "nombre_servicio": servicio.nombre_servicio,
            "descripcion": servicio.descripcion,
            "precio": servicio.precio,
            "duracion_minutos": servicio.duracion_minutos,
            "visible_online": servicio.visible_online,
            "activo": servicio.activo,
        }

    @staticmethod
    def _to_service(row: dict) -> Service:
        return Service(
            id=row["id"],
            nombre_servicio=row["nombre_servicio"],
            descripcion=row["descripcion"],
            precio=Decimal(row["precio"]),
            duracion_minutos=row["duracion_minutos"],
            visible_online=row["visible_online"],
            activo=row["activo"],
        )