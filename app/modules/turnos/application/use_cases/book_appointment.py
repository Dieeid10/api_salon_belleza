from datetime import tzinfo

from app.modules.turnos.application.dto import AppointmentResult, BookAppointmentCommand
from app.modules.turnos.application.ports import AppointmentsUnitOfWork, Clock
from app.modules.turnos.application.use_cases._comunes import (
    load_services, verify_professional,
)
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.availability import is_available
from app.modules.turnos.domain.entities import DetalleTurno, Turno
from app.modules.turnos.domain.errors import TimeSlotUnavailable


class BookAppointment:
    def __init__(self, uow: AppointmentsUnitOfWork, zona: tzinfo, clock: Clock) -> None:
        self._uow = uow
        self._zona = zona
        self._clock = clock

    def execute(self, command: BookAppointmentCommand) -> AppointmentResult:
        ahora = self._clock()
        # Todo lo que sigue es una sola transacción, si algo falla, no queda nada guardado
        with self._uow as uow:
            verify_professional(uow, command.profesional_id)
            servicios = load_services(uow, command.servicio_ids)
            detalles = [
                DetalleTurno(s.id, s.nombre, s.duracion_min, s.precio) for s in servicios
            ]

            cliente_id = uow.clients.get_or_create(
                command.nombre, command.apellido, command.telefono
            )
            turno = Turno.schedule(
                cliente_id, command.profesional_id, command.inicio, detalles, ahora
            )

            fecha = turno.franja.inicio.astimezone(self._zona).date()
            jornada = uow.schedule.get_schedule(command.profesional_id, fecha)
            ocupadas = uow.appointments.list_busy_slots(
                command.profesional_id, turno.franja.inicio, turno.franja.fin
            )
            if not is_available(turno.franja, jornada, ocupadas):
                raise TimeSlotUnavailable()

            # Si otra reserva se coló en el medio, el repositorio traduce
            # la violación de la restricción EXCLUDE a HorarioNoDisponible
            return to_result(uow.appointments.create(turno))