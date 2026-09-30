from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import Depends

from app.modules.turnos.application.use_cases.cambiar_estado_turno import CambiarEstadoTurno
from app.modules.turnos.application.use_cases.cancelar_turno import CancelarTurno
from app.modules.turnos.application.use_cases.consultar_disponibilidad import ConsultarDisponibilidad
from app.modules.turnos.application.use_cases.listar_turnos import ListarTurnos
from app.modules.turnos.application.use_cases.obtener_turno import ObtenerTurno
from app.modules.turnos.application.use_cases.reservar_turno import ReservarTurno
from app.modules.turnos.infrastructure.persistence.unit_of_work import PsycopgTurnosUnitOfWork
from app.shared.infrastructure.config import settings

ZONA = ZoneInfo(settings.zona_horaria)


def reloj() -> datetime:
    return datetime.now(timezone.utc)


def get_uow() -> PsycopgTurnosUnitOfWork:
    return PsycopgTurnosUnitOfWork(ZONA)  # uno nuevo por request


def get_consultar_disponibilidad(uow=Depends(get_uow)) -> ConsultarDisponibilidad:
    return ConsultarDisponibilidad(uow, reloj)

def get_reservar(uow=Depends(get_uow)) -> ReservarTurno:
    return ReservarTurno(uow, ZONA, reloj)

def get_cancelar(uow=Depends(get_uow)) -> CancelarTurno:
    return CancelarTurno(uow, reloj)

def get_cambiar_estado(uow=Depends(get_uow)) -> CambiarEstadoTurno:
    return CambiarEstadoTurno(uow, reloj)

def get_obtener(uow=Depends(get_uow)) -> ObtenerTurno:
    return ObtenerTurno(uow)

def get_listar(uow=Depends(get_uow)) -> ListarTurnos:
    return ListarTurnos(uow, ZONA)