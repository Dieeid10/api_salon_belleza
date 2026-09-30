from datetime import datetime, time, timedelta, tzinfo
from app.modules.turnos.application.dto import ListarTurnosQuery, TurnoResult
from app.modules.turnos.application.ports import TurnosUnitOfWork
from app.modules.turnos.application.use_cases._mapper import to_result

class ListarTurnos:
    def __init__(self, uow: TurnosUnitOfWork, zona: tzinfo) -> None:
        self._uow = uow
        self._zona = zona

    def execute(self, q: ListarTurnosQuery) -> list[TurnoResult]:
        # Las fechas son del día del salón, no de UTC
        desde = datetime.combine(q.desde, time.min, tzinfo=self._zona)
        hasta = datetime.combine(q.hasta + timedelta(days=1), time.min, tzinfo=self._zona)
        with self._uow as uow:
            turnos = uow.turnos.listar(desde, hasta, q.profesional_id, q.estado)
            return [to_result(t) for t in turnos]