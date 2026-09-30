import logging
from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.shared.infrastructure.config import settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, url: str) -> None:
        self._pool = ConnectionPool(
            url,
            min_size=0,
            max_size=3,
            open=False,
            kwargs={"prepare_threshold": None, "row_factory": dict_row},
        )

    def open(self) -> None:
        self._pool.open()
        logger.info("Pool de conexiones abierto")

    def close(self) -> None:
        self._pool.close()
        logger.info("Pool de conexiones cerrado")

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        """Commit al salir, rollback si hay excepción."""
        with self._pool.connection() as conn:
            yield conn


db = Database(settings.database_url)