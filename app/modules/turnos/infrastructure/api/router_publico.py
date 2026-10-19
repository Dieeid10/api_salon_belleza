from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.modules.turnos.application.dto import (
    BookAppointmentCommand, CheckAvailabilityQuery,
)
from app.modules.turnos.application.use_cases.check_appointment_availability import CheckAppointmentAvailability
from app.modules.turnos.application.use_cases.book_appointment import BookAppointment
from app.modules.turnos.infrastructure.api.dependencies import (
    get_availability_use_case, get_booking_use_case,
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
    uc: CheckAppointmentAvailability = Depends(get_availability_use_case),
):
    q = CheckAvailabilityQuery(profesional_id, servicio_ids, fecha)
    return asdict(uc.execute(q))


@router.post("/", response_model=TurnoPublicoResponse, status_code=status.HTTP_201_CREATED)
def reservar(body: ReservarTurnoRequest, uc: BookAppointment = Depends(get_booking_use_case)):
    return asdict(uc.execute(BookAppointmentCommand(**body.model_dump())))