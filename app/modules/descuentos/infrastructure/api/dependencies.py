from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.descuentos.application.use_cases import DescuentosUseCases
from app.modules.descuentos.infrastructure.persistence.descuento_repository import (
    PsycopgDescuentoRepository,
)
from app.modules.servicios.infrastructure.persistence.servicio_repository import (
    PsycopgServicioRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_use_cases(conn: Connection = Depends(get_conn)) -> DescuentosUseCases:
    return DescuentosUseCases(
        PsycopgDescuentoRepository(conn),
        PsycopgServicioRepository(conn),
    )