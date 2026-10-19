from app.modules.turnos.application.dto import AppointmentResult
from app.modules.turnos.application.ports import AppointmentsUnitOfWork
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.errors import AppointmentNotFound

class GetAppointment:
    def __init__(self, uow: AppointmentsUnitOfWork) -> None:
        self._uow = uow

    def execute(self, turno_id: int) -> AppointmentResult:
        with self._uow as uow:
            turno = uow.appointments.get(turno_id)
            if turno is None:
                raise AppointmentNotFound()
            return to_result(turno)