"""Adaptadores entre los contratos de turnos y los módulos dueños de los datos."""

from datetime import date, datetime, tzinfo

from app.modules.clientes.infrastructure.persistence.client_repository import (
    PsycopgClientRepository,
)
from app.modules.profesionales.infrastructure.persistence.business_hours_repository import PsycopgBusinessHoursRepository
from app.modules.profesionales.infrastructure.persistence.professional_repository import (
    PsycopgProfessionalRepository,
)
from app.modules.servicios.infrastructure.persistence.service_repository import (
    PsycopgServiceRepository,
)
from app.modules.turnos.application.dto import ServiceInfo
from app.modules.turnos.domain.value_objects import TimeSlot


class PsycopgServiceCatalog:
    def __init__(self, repository: PsycopgServiceRepository) -> None:
        self._repository = repository

    def get_active(self, servicio_ids: list[int]) -> list[ServiceInfo]:
        return [
            ServiceInfo(
                servicio.id,
                servicio.nombre,
                servicio.duracion_min,
                servicio.precio,
            )
            for servicio in self._repository.get_active(servicio_ids)
        ]


class PsycopgClientRegistration:
    def __init__(self, repository: PsycopgClientRepository) -> None:
        self._repository = repository

    def get_or_create(self, nombre: str, apellido: str, telefono: str) -> int:
        return self._repository.get_or_create_for_reservation(
            nombre,
            apellido,
            telefono,
        )


class PsycopgProfessionalSchedule:
    def __init__(
        self,
        profesionales: PsycopgProfessionalRepository,
        horarios: PsycopgBusinessHoursRepository,
        zona: tzinfo,
    ) -> None:
        self._profesionales = profesionales
        self._horarios = horarios
        self._zona = zona

    def is_active(self, profesional_id: int) -> bool:
        return self._profesionales.is_active(profesional_id)

    def get_schedule(self, profesional_id: int, fecha: date) -> list[TimeSlot]:
        return [
            TimeSlot(
                datetime.combine(fecha, horario.hora_apertura, tzinfo=self._zona),
                datetime.combine(fecha, horario.hora_cierre, tzinfo=self._zona),
            )
            for horario in self._horarios.get_schedule(profesional_id, fecha)
        ]