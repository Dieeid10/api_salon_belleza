from app.modules.turnos.application.dto import TurnoResult
from app.modules.turnos.application.ports import TurnosUnitOfWork
from app.modules.turnos.application.use_cases._mapper import to_result
from app.modules.turnos.domain.errors import TurnoNoEncontrado

class ObtenerTurno:
    def __init__(self, uow: TurnosUnitOfWork) -> None:
        self._uow = uow

    def execute(self, turno_id: int) -> TurnoResult:
        with self._uow as uow:
            turno = uow.turnos.obtener(turno_id)
            if turno is None:
                raise TurnoNoEncontrado()
            return to_result(turno)