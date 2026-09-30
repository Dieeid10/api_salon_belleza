from app.modules.turnos.application.dto import TurnoResult
from app.modules.turnos.application.ports import Reloj, TurnosUnitOfWork
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.errors import TurnoNoEncontrado

class CancelarTurno:
    def __init__(self, uow: TurnosUnitOfWork, reloj: Reloj) -> None:
        self._uow = uow
        self._reloj = reloj

    def execute(self, turno_id: int) -> TurnoResult:
        with self._uow as uow:
            turno = uow.turnos.obtener(turno_id, bloquear=True)
            if turno is None:
                raise TurnoNoEncontrado()
            turno.cancelar(self._reloj())
            uow.turnos.actualizar_estado(turno)
            return to_result(turno)