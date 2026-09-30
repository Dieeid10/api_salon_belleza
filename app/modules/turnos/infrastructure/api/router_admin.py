from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, status

from app.modules.turnos.application.dto import (
    CambiarEstadoCommand, ListarTurnosQuery, ReservarTurnoCommand,
)
from app.modules.turnos.application.use_cases.cambiar_estado_turno import CambiarEstadoTurno
from app.modules.turnos.application.use_cases.cancelar_turno import CancelarTurno
from app.modules.turnos.application.use_cases.listar_turnos import ListarTurnos
from app.modules.turnos.application.use_cases.obtener_turno import ObtenerTurno
from app.modules.turnos.application.use_cases.reservar_turno import ReservarTurno
from app.modules.turnos.domain.value_objects import EstadoTurno
from app.modules.turnos.infrastructure.api.dependencies import (
    get_cambiar_estado, get_cancelar, get_listar, get_obtener, get_reservar,
)
from app.modules.turnos.infrastructure.api.schemas import (
    CambiarEstadoRequest, ReservarTurnoRequest, TurnoResponse,
)
from app.shared.security import require_role

# Todo el router exige personal autenticado
router = APIRouter(dependencies=[Depends(require_role("dueno", "vendedor"))])


@router.get("/", response_model=list[TurnoResponse])
def listar(
    desde: date,
    hasta: date,
    profesional_id: int | None = None,
    estado: EstadoTurno | None = None,
    uc: ListarTurnos = Depends(get_listar),
):
    resultados = uc.execute(ListarTurnosQuery(desde, hasta, profesional_id, estado))
    return [asdict(r) for r in resultados]


@router.get("/{turno_id}", response_model=TurnoResponse)
def obtener(turno_id: int, uc: ObtenerTurno = Depends(get_obtener)):
    return asdict(uc.execute(turno_id))


@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
def reservar(body: ReservarTurnoRequest, uc: ReservarTurno = Depends(get_reservar)):
    return asdict(uc.execute(ReservarTurnoCommand(**body.model_dump())))


@router.post("/{turno_id}/cancelar", response_model=TurnoResponse)
def cancelar(turno_id: int, uc: CancelarTurno = Depends(get_cancelar)):
    return asdict(uc.execute(turno_id))


@router.patch("/{turno_id}/estado", response_model=TurnoResponse)
def cambiar_estado(
    turno_id: int, body: CambiarEstadoRequest,
    uc: CambiarEstadoTurno = Depends(get_cambiar_estado),
):
    return asdict(uc.execute(CambiarEstadoCommand(turno_id, body.nuevo_estado)))