from datetime import tzinfo, timedelta

from app.modules.turnos.application.dto import (
    ConsultarDisponibilidadQuery, DisponibilidadResult,
)
from app.modules.turnos.application.ports import Reloj, TurnosUnitOfWork
from app.modules.turnos.application.use_cases._comunes import (
    cargar_servicios, verificar_profesional,
)
from app.modules.turnos.domain.disponibilidad import calcular_slots


class ConsultarDisponibilidad:
    def __init__(self, uow: TurnosUnitOfWork, reloj: Reloj) -> None:
        self._uow = uow
        self._reloj = reloj

    def execute(self, q: ConsultarDisponibilidadQuery) -> DisponibilidadResult:
        ahora = self._reloj()
        with self._uow as uow:
            verificar_profesional(uow, q.profesional_id)
            servicios = cargar_servicios(uow, q.servicio_ids)
            duracion_min = sum(s.duracion_min for s in servicios)

            jornada = uow.agenda.jornada(q.profesional_id, q.fecha)
            horarios = []
            if jornada:
                ocupadas = uow.turnos.listar_ocupados(
                    q.profesional_id,
                    desde=min(f.inicio for f in jornada),
                    hasta=max(f.fin for f in jornada),
                )
                horarios = calcular_slots(
                    jornada, ocupadas, timedelta(minutes=duracion_min), ahora
                )

        return DisponibilidadResult(
            profesional_id=q.profesional_id,
            fecha=q.fecha,
            duracion_min=duracion_min,
            horarios=horarios,
        )