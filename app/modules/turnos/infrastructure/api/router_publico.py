from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.modules.turnos.application.dto import (
    ConsultarDisponibilidadQuery, ReservarTurnoCommand,
)
from app.modules.turnos.application.use_cases.consultar_disponibilidad import ConsultarDisponibilidad
from app.modules.turnos.application.use_cases.reservar_turno import ReservarTurno
from app.modules.turnos.infrastructure.api.dependencies import (
    get_consultar_disponibilidad, get_reservar,
)
from app.modules.turnos.infrastructure.api.schemas import (
    DisponibilidadResponse, ReservarTurnoRequest, TurnoPublicoResponse,
)

# Acá van el rate limiting y el captcha: router = APIRouter(dependencies=[...])
router = APIRouter()


@router.get("/disponibilidad", response_model=DisponibilidadResponse)
def disponibilidad(
    profesional_id: int,
    fecha: date,
    servicio_ids: list[int] = Query(min_length=1),
    uc: ConsultarDisponibilidad = Depends(get_consultar_disponibilidad),
):
    q = ConsultarDisponibilidadQuery(profesional_id, servicio_ids, fecha)
    return asdict(uc.execute(q))


@router.post("/", response_model=TurnoPublicoResponse, status_code=status.HTTP_201_CREATED)
def reservar(body: ReservarTurnoRequest, uc: ReservarTurno = Depends(get_reservar)):
    return asdict(uc.execute(ReservarTurnoCommand(**body.model_dump())))