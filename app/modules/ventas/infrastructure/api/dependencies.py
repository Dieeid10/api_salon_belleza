from collections.abc import Iterator
from datetime import datetime, timezone

from fastapi import Depends
from psycopg import Connection

from app.modules.clientes.infrastructure.persistence.client_repository import (
    PsycopgClientRepository,
)
from app.modules.descuentos.infrastructure.persistence.discount_repository import (
    PsycopgDiscountRepository,
)
from app.modules.turnos.infrastructure.persistence.appointment_repository import (
    PsycopgAppointmentRepository,
)
from app.modules.ventas.application.use_cases import SaleUseCases
from app.modules.ventas.infrastructure.persistence.sale_repository import (
    PsycopgSaleRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def clock() -> datetime:
    return datetime.now(timezone.utc)


def get_use_cases(conn: Connection = Depends(get_conn)) -> SaleUseCases:
    return SaleUseCases(
        repo=PsycopgSaleRepository(conn),
        turnos=PsycopgAppointmentRepository(conn),
        clients=PsycopgClientRepository(conn),
        descuentos=PsycopgDiscountRepository(conn),
        reloj=clock,
    )