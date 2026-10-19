from datetime import tzinfo

from app.modules.turnos.infrastructure.persistence.gateways import (
    PsycopgProfessionalSchedule, PsycopgClientRegistration, PsycopgServiceCatalog,
)
from app.modules.turnos.infrastructure.persistence.appointment_repository import (
    PsycopgAppointmentRepository,
)
from app.modules.clientes.infrastructure.persistence.client_repository import (
    PsycopgClientRepository,
)
from app.modules.profesionales.infrastructure.persistence.business_hours_repository import (
    PsycopgBusinessHoursRepository,
)
from app.modules.profesionales.infrastructure.persistence.professional_repository import (
    PsycopgProfessionalRepository,
)
from app.modules.servicios.infrastructure.persistence.service_repository import (
    PsycopgServiceRepository,
)
from app.shared.infrastructure.db.database import db


class PsycopgAppointmentsUnitOfWork:
    """Una conexión y una transacción compartidas por todos los repositorios."""

    def __init__(self, timezone: tzinfo) -> None:
        self._timezone = timezone

    def __enter__(self) -> "PsycopgAppointmentsUnitOfWork":
        self._tx = db.transaction()
        conn = self._tx.__enter__()  # toma una conexión del pool
        clients = PsycopgClientRepository(conn)
        professionals = PsycopgProfessionalRepository(conn)
        self.appointments = PsycopgAppointmentRepository(conn)
        self.services = PsycopgServiceCatalog(PsycopgServiceRepository(conn))
        self.clients = PsycopgClientRegistration(clients)
        self.schedule = PsycopgProfessionalSchedule(
            professionals,
            PsycopgBusinessHoursRepository(conn),
            self._timezone,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> bool | None:
        # Sin excepción: commit. Con excepción: rollback y se propaga al handler HTTP
        return self._tx.__exit__(exc_type, exc, tb)