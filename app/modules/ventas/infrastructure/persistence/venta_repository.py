from decimal import Decimal

from psycopg import Connection

from app.modules.ventas.domain.entities import DetalleVenta, Venta
from app.shared.infrastructure.db.crud import Crud

TABLE = "ventas"
DETAIL_TABLE = "detalle_ventas"


class PsycopgVentaRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn
        self._crud = Crud(conn)

    def crear(self, venta: Venta) -> Venta:
        row = self._crud.insert(
            TABLE,
            {
                "fecha_hora": venta.fecha_hora,
                "cliente_id": venta.cliente_id,
                "empleado_id": venta.empleado_id,
                "turno_id": venta.turno_id,
                "descuento_chisme_id": venta.descuento_chisme_id,
                "chisme_pct": venta.chisme_pct,
                "chisme_detalle": venta.chisme_detalle,
            },
        )
        venta.id = row["id"]
        for detalle in venta.detalles:
            self._crud.insert(
                DETAIL_TABLE,
                {
                    "venta_id": venta.id,
                    "servicio_id": detalle.servicio_id,
                    "descuento_id": detalle.descuento_id,
                    "precio_lista": detalle.precio_lista,
                    "descuento_pct": detalle.descuento_pct,
                    "precio_cobrado": detalle.precio_cobrado,
                },
            )
        return venta

    def obtener(self, venta_id: int) -> Venta | None:
        row = self._crud.select(TABLE, venta_id)
        if row is None:
            return None
        return self._to_entity(row, self._detalles([venta_id]).get(venta_id, []))

    def listar(self) -> list[Venta]:
        rows = self._conn.execute(
            "SELECT * FROM ventas ORDER BY fecha_hora DESC, id DESC"
        ).fetchall()
        detalles = self._detalles([row["id"] for row in rows])
        return [self._to_entity(row, detalles.get(row["id"], [])) for row in rows]

    def obtener_por_turno(self, turno_id: int) -> Venta | None:
        row = self._conn.execute(
            "SELECT id FROM ventas WHERE turno_id = %s ORDER BY id LIMIT 1",
            (turno_id,),
        ).fetchone()
        return self.obtener(row["id"]) if row else None

    def _detalles(self, venta_ids: list[int]) -> dict[int, list[DetalleVenta]]:
        if not venta_ids:
            return {}
        rows = self._conn.execute(
            """
            SELECT venta_id, servicio_id, descuento_id, precio_lista,
                   descuento_pct, precio_cobrado
            FROM detalle_ventas
            WHERE venta_id = ANY(%s)
            ORDER BY venta_id, id
            """,
            (venta_ids,),
        ).fetchall()
        resultado: dict[int, list[DetalleVenta]] = {}
        for row in rows:
            resultado.setdefault(row["venta_id"], []).append(
                DetalleVenta(
                    servicio_id=row["servicio_id"],
                    descuento_id=row["descuento_id"],
                    precio_lista=(
                        Decimal(row["precio_lista"])
                        if row["precio_lista"] is not None
                        else None
                    ),
                    descuento_pct=Decimal(row["descuento_pct"]),
                    precio_cobrado=Decimal(row["precio_cobrado"]),
                )
            )
        return resultado

    @staticmethod
    def _to_entity(row: dict, detalles: list[DetalleVenta]) -> Venta:
        return Venta(
            id=row["id"],
            fecha_hora=row["fecha_hora"],
            cliente_id=row["cliente_id"],
            empleado_id=row["empleado_id"],
            turno_id=row["turno_id"],
            descuento_chisme_id=row["descuento_chisme_id"],
            chisme_pct=Decimal(row["chisme_pct"]),
            chisme_detalle=row["chisme_detalle"],
            detalles=detalles,
        )