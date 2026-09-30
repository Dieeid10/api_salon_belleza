from datetime import date
from decimal import Decimal

from psycopg import Connection
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.modules.descuentos.domain.entities import Descuento, TipoDescuento
from app.modules.descuentos.domain.errors import (
    DescuentoChismeYaConfigurado,
    ServicioDescuentoNoEncontrado,
)
from app.shared.infrastructure.db.crud import Crud

TABLE = "descuentos"


class PsycopgDescuentoRepository:
    def __init__(self, conn: Connection) -> None:
        self._crud = Crud(conn)

    def crear(self, descuento: Descuento) -> Descuento:
        try:
            row = self._crud.insert(TABLE, self._to_data(descuento))
        except UniqueViolation as error:
            self._raise_unique_conflict(error)
        except ForeignKeyViolation as error:
            raise ServicioDescuentoNoEncontrado() from error
        return self._to_entity(row)

    def obtener(self, descuento_id: int) -> Descuento | None:
        row = self._crud.select(TABLE, descuento_id)
        return self._to_entity(row) if row else None

    def listar(self) -> list[Descuento]:
        rows = self._crud.select_all(TABLE)
        return [self._to_entity(row) for row in rows]

    def obtener_chisme(self) -> Descuento | None:
        rows = self._crud.select_all(TABLE, "tipo = %s", (TipoDescuento.CHISME.value,))
        return self._to_entity(rows[0]) if rows else None

    def listar_publicos(self, fecha: date) -> list[Descuento]:
        rows = self._crud.select_all(
            TABLE,
            "tipo = %s AND activo = %s "
            "AND (fecha_inicio IS NULL OR fecha_inicio <= %s) "
            "AND (fecha_fin IS NULL OR fecha_fin >= %s)",
            (TipoDescuento.SERVICIO.value, True, fecha, fecha),
        )
        return [self._to_entity(row) for row in rows]

    def actualizar(self, descuento: Descuento) -> Descuento:
        if descuento.id is None:
            raise ValueError("No se puede actualizar un descuento sin id")
        try:
            row = self._crud.update(TABLE, descuento.id, self._to_data(descuento))
        except UniqueViolation as error:
            self._raise_unique_conflict(error)
        except ForeignKeyViolation as error:
            raise ServicioDescuentoNoEncontrado() from error
        if row is None:
            raise ValueError("El descuento dejó de existir durante la actualización")
        return self._to_entity(row)

    @staticmethod
    def _to_data(descuento: Descuento) -> dict:
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
    def _to_entity(row: dict) -> Descuento:
        return Descuento(
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
            raise DescuentoChismeYaConfigurado() from error
        raise error