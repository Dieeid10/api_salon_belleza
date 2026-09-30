from datetime import tzinfo

from app.modules.turnos.application.dto import ReservarTurnoCommand, TurnoResult
from app.modules.turnos.application.ports import Reloj, TurnosUnitOfWork
from app.modules.turnos.application.use_cases._comunes import (
    cargar_servicios, verificar_profesional,
)
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.disponibilidad import esta_disponible
from app.modules.turnos.domain.entities import DetalleTurno, Turno
from app.modules.turnos.domain.errors import HorarioNoDisponible


class ReservarTurno:
    def __init__(self, uow: TurnosUnitOfWork, zona: tzinfo, reloj: Reloj) -> None:
        self._uow = uow
        self._zona = zona
        self._reloj = reloj

    def execute(self, cmd: ReservarTurnoCommand) -> TurnoResult:
        ahora = self._reloj()
        # Todo lo que sigue es una sola transacción: si algo falla, no queda nada guardado
        with self._uow as uow:
            verificar_profesional(uow, cmd.profesional_id)
            servicios = cargar_servicios(uow, cmd.servicio_ids)
            detalles = [
                DetalleTurno(s.id, s.nombre, s.duracion_min, s.precio) for s in servicios
            ]

            cliente_id = uow.clientes.obtener_o_crear(
                cmd.nombre, cmd.apellido, cmd.telefono
            )
            turno = Turno.agendar(  # valida futuro y calcula el fin
                cliente_id, cmd.profesional_id, cmd.inicio, detalles, ahora
            )

            fecha = turno.franja.inicio.astimezone(self._zona).date()
            jornada = uow.agenda.jornada(cmd.profesional_id, fecha)
            ocupadas = uow.turnos.listar_ocupados(
                cmd.profesional_id, turno.franja.inicio, turno.franja.fin
            )
            if not esta_disponible(turno.franja, jornada, ocupadas):
                raise HorarioNoDisponible()

            # Si otra reserva se coló en el medio, el repositorio traduce
            # la violación de la restricción EXCLUDE a HorarioNoDisponible
            return to_result(uow.turnos.crear(turno))