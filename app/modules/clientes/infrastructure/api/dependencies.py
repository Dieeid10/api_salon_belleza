from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.clientes.application.use_cases import ClientesUseCases
from app.modules.clientes.infrastructure.persistence.cliente_repository import (
    PsycopgClienteRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_repo(conn: Connection = Depends(get_conn)) -> PsycopgClienteRepository:
    return PsycopgClienteRepository(conn)


def get_use_cases(
    repo: PsycopgClienteRepository = Depends(get_repo),
) -> ClientesUseCases:
    return ClientesUseCases(repo)