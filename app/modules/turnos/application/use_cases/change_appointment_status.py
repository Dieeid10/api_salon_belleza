from app.modules.turnos.application.dto import AppointmentResult, ChangeAppointmentStatusCommand
from app.modules.turnos.application.ports import AppointmentsUnitOfWork, Clock
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.errors import AppointmentNotFound

class ChangeAppointmentStatus:
    def __init__(self, uow: AppointmentsUnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def execute(self, command: ChangeAppointmentStatusCommand) -> AppointmentResult:
        with self._uow as uow:
            turno = uow.appointments.get(command.turno_id, lock=True)
            if turno is None:
                raise AppointmentNotFound()
            turno.change_status(command.nuevo_estado, self._clock())
            uow.appointments.update_status(turno)
            return to_result(turno)