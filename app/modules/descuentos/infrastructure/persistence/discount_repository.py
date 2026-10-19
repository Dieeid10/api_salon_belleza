from datetime import date
from decimal import Decimal

from psycopg import Connection
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.modules.descuentos.domain.entities import Discount, TipoDescuento
from app.modules.descuentos.domain.errors import (
    DiscountServiceNotFound,
    GossipDiscountAlreadyConfigured,
)
from app.shared.infrastructure.db.crud import Crud

TABLE = "descuentos"


class PsycopgDiscountRepository:
    def __init__(self, conn: Connection) -> None:
        self._crud = Crud(conn)

    def create(self, descuento: Discount) -> Discount:
        try:
            row = self._crud.insert(TABLE, self._to_database_record(descuento))
        except UniqueViolation as error:
            self._raise_unique_conflict(error)
        except ForeignKeyViolation as error:
            raise DiscountServiceNotFound() from error
        return self._to_discount(row)

    def get(self, descuento_id: int) -> Discount | None:
        row = self._crud.select(TABLE, descuento_id)
        return self._to_discount(row) if row else None

    def list_all(self) -> list[Discount]:
        rows = self._crud.select_all(TABLE)
        return [self._to_discount(row) for row in rows]

    def get_gossip_discount(self) -> Discount | None:
        rows = self._crud.select_all(TABLE, "tipo = %s", (TipoDescuento.CHISME.value,))
        return self._to_discount(rows[0]) if rows else None

    def list_public(self, fecha: date) -> list[Discount]:
        rows = self._crud.select_all(
            TABLE,
            "tipo = %s AND activo = %s "
            "AND (fecha_inicio IS NULL OR fecha_inicio <= %s) "
            "AND (fecha_fin IS NULL OR fecha_fin >= %s)",
            (TipoDescuento.SERVICIO.value, True, fecha, fecha),
        )
        return [self._to_discount(row) for row in rows]

    def update(self, descuento: Discount) -> Discount:
        if descuento.id is None:
            raise ValueError("No se puede actualizar un descuento sin id")
        try:
            row = self._crud.update(TABLE, descuento.id, self._to_database_record(descuento))
        except UniqueViolation as error:
            self._raise_unique_conflict(error)
        except ForeignKeyViolation as error:
            raise DiscountServiceNotFound() from error
        if row is None:
            raise ValueError("El descuento dejó de existir durante la actualización")
        return self._to_discount(row)

    @staticmethod
    def _to_database_record(descuento: Discount) -> dict:
        return {
            "nombre": descuento.nombre,
            "tipo": descuento.tipo.value,
            "servicio_id": descuento.servicio_id,
            "porcentaje": descuento.porcentaje,
            "fecha_inicio": descuento.fecha_inicio,
            "fecha_fin": descuento.fecha_fin,
            "activo": descuento.activo,
        }

    @staticmethod
    def _to_discount(row: dict) -> Discount:
        return Discount(
            id=row["id"],
            nombre=row["nombre"],
            tipo=TipoDescuento(row["tipo"]),
            servicio_id=row["servicio_id"],
            porcentaje=Decimal(row["porcentaje"]),
            fecha_inicio=row["fecha_inicio"],
            fecha_fin=row["fecha_fin"],
            activo=row["activo"],
        )

    @staticmethod
    def _raise_unique_conflict(error: UniqueViolation) -> None:
        if error.diag.constraint_name == "uq_descuento_chisme":
            raise GossipDiscountAlreadyConfigured() from error
        raise error