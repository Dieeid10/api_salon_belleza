from app.modules.turnos.application.dto import ServiceInfo
from app.modules.turnos.application.ports import AppointmentsUnitOfWork
from app.modules.turnos.domain.errors import (
    AppointmentWithoutServices, ProfessionalUnavailable, ServiceUnavailable,
)


def verify_professional(uow: AppointmentsUnitOfWork, professional_id: int) -> None:
    if not uow.schedule.is_active(professional_id):
        raise ProfessionalUnavailable()


def load_services(uow: AppointmentsUnitOfWork, service_ids: list[int]) -> list[ServiceInfo]:
    ids = list(dict.fromkeys(service_ids))
    if not ids:
        raise AppointmentWithoutServices()
    services = uow.services.get_active(ids)
    if len(services) != len(ids):
        raise ServiceUnavailable()
    return services