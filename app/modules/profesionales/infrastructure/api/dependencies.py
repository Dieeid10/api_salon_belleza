from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.profesionales.application.use_cases import ProfesionalesUseCases
from app.modules.profesionales.infrastructure.persistence.profesional_repository import (
    PsycopgProfesionalRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_repo(conn: Connection = Depends(get_conn)) -> PsycopgProfesionalRepository:
    return PsycopgProfesionalRepository(conn)


def get_use_cases(repo: PsycopgProfesionalRepository = Depends(get_repo)) -> ProfesionalesUseCases:
    return ProfesionalesUseCases(repo)