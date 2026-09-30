from app.modules.turnos.application.dto import CambiarEstadoCommand, TurnoResult
from app.modules.turnos.application.ports import Reloj, TurnosUnitOfWork
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.errors import TurnoNoEncontrado

class CambiarEstadoTurno:
    def __init__(self, uow: TurnosUnitOfWork, reloj: Reloj) -> None:
        self._uow = uow
        self._reloj = reloj

    def execute(self, cmd: CambiarEstadoCommand) -> TurnoResult:
        with self._uow as uow:
            turno = uow.turnos.obtener(cmd.turno_id, bloquear=True)
            if turno is None:
                raise TurnoNoEncontrado()
            turno.cambiar_estado(cmd.nuevo_estado, self._reloj())
            uow.turnos.actualizar_estado(turno)
            return to_result(turno)