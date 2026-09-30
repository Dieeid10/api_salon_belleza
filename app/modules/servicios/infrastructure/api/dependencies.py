from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.servicios.application.use_cases import ServiciosUseCases
from app.modules.servicios.infrastructure.persistence.servicio_repository import (
    PsycopgServicioRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_repo(conn: Connection = Depends(get_conn)) -> PsycopgServicioRepository:
    return PsycopgServicioRepository(conn)


def get_use_cases(
    repo: PsycopgServicioRepository = Depends(get_repo),
) -> ServiciosUseCases:
    return ServiciosUseCases(repo)