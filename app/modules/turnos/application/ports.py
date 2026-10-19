from collections.abc import Callable
from datetime import date, datetime
from typing import Protocol

from app.modules.turnos.application.dto import AppointmentSaleInfo, ServiceInfo
from app.modules.turnos.domain.entities import Turno
from app.modules.turnos.domain.value_objects import EstadoTurno, TimeSlot

Clock = Callable[[], datetime]


class AppointmentRepository(Protocol):
    def create(self, appointment: Turno) -> Turno: ...
    def get(self, appointment_id: int, lock: bool = False) -> Turno | None: ...
    def update_status(self, appointment: Turno) -> None: ...
    def list_busy_slots(
        self, professional_id: int, start: datetime, end: datetime
    ) -> list[TimeSlot]: ...
    def list_all(
        self,
        start: datetime,
        end: datetime,
        professional_id: int | None = None,
        status: EstadoTurno | None = None,
    ) -> list[Turno]: ...
    def get_for_sale(
        self, appointment_id: int, lock: bool = False
    ) -> AppointmentSaleInfo | None: ...


class ServiceCatalog(Protocol):
    def get_active(self, service_ids: list[int]) -> list[ServiceInfo]: ...


class ClientRegistration(Protocol):
    def get_or_create(self, first_name: str, last_name: str, phone: str) -> int: ...


class ProfessionalSchedule(Protocol):
    def is_active(self, professional_id: int) -> bool: ...
    def get_schedule(self, professional_id: int, date: date) -> list[TimeSlot]: ...


class AppointmentsUnitOfWork(Protocol):
    appointments: AppointmentRepository
    services: ServiceCatalog
    clients: ClientRegistration
    schedule: ProfessionalSchedule

    def __enter__(self) -> "AppointmentsUnitOfWork": ...
    def __exit__(self, exc_type, exc, tb) -> bool | None: ...