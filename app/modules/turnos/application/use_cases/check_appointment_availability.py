from datetime import tzinfo, timedelta

from app.modules.turnos.application.dto import (
    AvailabilityResult, CheckAvailabilityQuery,
)
from app.modules.turnos.application.ports import AppointmentsUnitOfWork, Clock
from app.modules.turnos.application.use_cases._comunes import (
    load_services, verify_professional,
)
from app.modules.turnos.domain.availability import calculate_slots


class CheckAppointmentAvailability:
    def __init__(self, uow: AppointmentsUnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def execute(self, query: CheckAvailabilityQuery) -> AvailabilityResult:
        ahora = self._clock()
        with self._uow as uow:
            verify_professional(uow, query.profesional_id)
            servicios = load_services(uow, query.servicio_ids)
            duracion_min = sum(s.duracion_min for s in servicios)

            jornada = uow.schedule.get_schedule(query.profesional_id, query.fecha)
            horarios = []
            if jornada:
                ocupadas = uow.appointments.list_busy_slots(
                    query.profesional_id,
                    desde=min(f.inicio for f in jornada),
                    hasta=max(f.fin for f in jornada),
                )
                horarios = calculate_slots(
                    jornada, ocupadas, timedelta(minutes=duracion_min), ahora
                )

        return AvailabilityResult(
            profesional_id=query.profesional_id,
            fecha=query.fecha,
            duracion_min=duracion_min,
            horarios=horarios,
        )