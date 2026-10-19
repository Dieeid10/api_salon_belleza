from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.clientes.application.use_cases import ClientUseCases
from app.modules.clientes.infrastructure.persistence.client_repository import (
    PsycopgClientRepository,
)
from app.shared.infrastructure.db.database import db


def get_connection() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_repository(
    connection: Connection = Depends(get_connection),
) -> PsycopgClientRepository:
    return PsycopgClientRepository(connection)


def get_use_cases(
    repository: PsycopgClientRepository = Depends(get_repository),
) -> ClientUseCases:
    return ClientUseCases(repository)