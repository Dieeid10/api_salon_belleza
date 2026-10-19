from datetime import datetime, time, timedelta, tzinfo
from app.modules.turnos.application.dto import AppointmentResult, ListAppointmentsQuery
from app.modules.turnos.application.ports import AppointmentsUnitOfWork
from app.modules.turnos.application.use_cases._mapper import to_result

class ListAppointments:
    def __init__(self, uow: AppointmentsUnitOfWork, zona: tzinfo) -> None:
        self._uow = uow
        self._zona = zona

    def execute(self, q: ListAppointmentsQuery) -> list[AppointmentResult]:
        # Las fechas son del día del salón, no de UTC
        desde = datetime.combine(q.desde, time.min, tzinfo=self._zona)
        hasta = datetime.combine(q.hasta + timedelta(days=1), time.min, tzinfo=self._zona)
        with self._uow as uow:
            turnos = uow.appointments.list_all(desde, hasta, q.profesional_id, q.estado)
            return [to_result(t) for t in turnos]