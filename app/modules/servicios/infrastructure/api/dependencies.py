from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.servicios.application.use_cases import ServiceUseCases
from app.modules.servicios.infrastructure.persistence.service_repository import (
    PsycopgServiceRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_repo(conn: Connection = Depends(get_conn)) -> PsycopgServiceRepository:
    return PsycopgServiceRepository(conn)


def get_use_cases(
    repo: PsycopgServiceRepository = Depends(get_repo),
) -> ServiceUseCases:
    return ServiceUseCases(repo)