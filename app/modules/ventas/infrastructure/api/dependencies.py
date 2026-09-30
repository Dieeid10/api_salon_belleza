from collections.abc import Iterator
from datetime import datetime, timezone

from fastapi import Depends
from psycopg import Connection

from app.modules.clientes.infrastructure.persistence.cliente_repository import (
    PsycopgClienteRepository,
)
from app.modules.descuentos.infrastructure.persistence.descuento_repository import (
    PsycopgDescuentoRepository,
)
from app.modules.turnos.infrastructure.persistence.turno_repository import (
    PsycopgTurnoRepository,
)
from app.modules.ventas.application.use_cases import VentasUseCases
from app.modules.ventas.infrastructure.persistence.venta_repository import (
    PsycopgVentaRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def reloj() -> datetime:
    return datetime.now(timezone.utc)


def get_use_cases(conn: Connection = Depends(get_conn)) -> VentasUseCases:
    return VentasUseCases(
        repo=PsycopgVentaRepository(conn),
        turnos=PsycopgTurnoRepository(conn),
        clientes=PsycopgClienteRepository(conn),
        descuentos=PsycopgDescuentoRepository(conn),
        reloj=reloj,
    )