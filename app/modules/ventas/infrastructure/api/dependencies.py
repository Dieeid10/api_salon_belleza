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
from app.modules.ventas.infrastructure.persistence.gateways import (
    PsycopgAppointmentSaleLookup,
    PsycopgClientLookup,
    PsycopgGossipDiscountLookup,
)
from app.modules.ventas.infrastructure.persistence.sale_repository import (
    PsycopgSaleRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    """Entrega una conexión dentro de una transacción para la petición."""
    with db.transaction() as conn:
        yield conn


def clock() -> datetime:
    """Proporciona la hora actual en UTC para registrar la venta."""
    return datetime.now(timezone.utc)


def get_use_cases(conn: Connection = Depends(get_conn)) -> SaleUseCases:
    """Construye el caso de uso y conecta sus puertos con adaptadores reales."""
    client_repository = PsycopgClientRepository(conn)
    discount_repository = PsycopgDiscountRepository(conn)
    return SaleUseCases(
        repo=PsycopgSaleRepository(conn),
        turnos=PsycopgAppointmentSaleLookup(
            PsycopgAppointmentRepository(conn)
        ),
        clients=PsycopgClientLookup(client_repository),
        descuentos=PsycopgGossipDiscountLookup(discount_repository),
        reloj=clock,
    )