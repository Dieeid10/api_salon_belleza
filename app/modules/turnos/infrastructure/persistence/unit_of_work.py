from datetime import tzinfo

from app.modules.turnos.infrastructure.persistence.gateways import (
    PsycopgAgendaProfesional, PsycopgClienteRegistro, PsycopgServicioCatalogo,
)
from app.modules.turnos.infrastructure.persistence.turno_repository import (
    PsycopgTurnoRepository,
)
from app.modules.clientes.infrastructure.persistence.cliente_repository import (
    PsycopgClienteRepository,
)
from app.modules.profesionales.infrastructure.persistence.horario_atencion_repository import (
    PsycopgHorarioAtencionRepository,
)
from app.modules.profesionales.infrastructure.persistence.profesional_repository import (
    PsycopgProfesionalRepository,
)
from app.modules.servicios.infrastructure.persistence.servicio_repository import (
    PsycopgServicioRepository,
)
from app.shared.infrastructure.db.database import db


class PsycopgTurnosUnitOfWork:
    """Una conexión y una transacción compartidas por todos los repositorios."""

    def __init__(self, zona: tzinfo) -> None:
        self._zona = zona

    def __enter__(self) -> "PsycopgTurnosUnitOfWork":
        self._tx = db.transaction()
        conn = self._tx.__enter__()  # toma una conexión del pool
        clientes = PsycopgClienteRepository(conn)
        profesionales = PsycopgProfesionalRepository(conn)
        self.turnos = PsycopgTurnoRepository(conn)
        self.servicios = PsycopgServicioCatalogo(PsycopgServicioRepository(conn))
        self.clientes = PsycopgClienteRegistro(clientes)
        self.agenda = PsycopgAgendaProfesional(
            profesionales,
            PsycopgHorarioAtencionRepository(conn),
            self._zona,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> bool | None:
        # Sin excepción: commit. Con excepción: rollback y se propaga al handler HTTP
        return self._tx.__exit__(exc_type, exc, tb)