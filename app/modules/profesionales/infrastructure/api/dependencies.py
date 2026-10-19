from collections.abc import Iterator

from fastapi import Depends
from psycopg import Connection

from app.modules.profesionales.application.use_cases import ProfessionalUseCases
from app.modules.profesionales.infrastructure.persistence.professional_repository import (
    PsycopgProfessionalRepository,
)
from app.shared.infrastructure.db.database import db


def get_conn() -> Iterator[Connection]:
    with db.transaction() as conn:
        yield conn


def get_repo(conn: Connection = Depends(get_conn)) -> PsycopgProfessionalRepository:
    return PsycopgProfessionalRepository(conn)


def get_use_cases(repo: PsycopgProfessionalRepository = Depends(get_repo)) -> ProfessionalUseCases:
    return ProfessionalUseCases(repo)