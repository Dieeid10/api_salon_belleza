from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, status

from app.modules.turnos.application.dto import (
    BookAppointmentCommand, ChangeAppointmentStatusCommand, ListAppointmentsQuery,
)
from app.modules.turnos.application.use_cases.change_appointment_status import ChangeAppointmentStatus
from app.modules.turnos.application.use_cases.cancel_appointment import CancelAppointment
from app.modules.turnos.application.use_cases.list_appointments import ListAppointments
from app.modules.turnos.application.use_cases.get_appointment import GetAppointment
from app.modules.turnos.application.use_cases.book_appointment import BookAppointment
from app.modules.turnos.domain.value_objects import EstadoTurno
from app.modules.turnos.infrastructure.api.dependencies import (
    get_appointment_use_case, get_booking_use_case,
    get_cancel_appointment_use_case, get_change_status_use_case,
    get_list_appointments_use_case,
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
    uc: ListAppointments = Depends(get_list_appointments_use_case),
):
    resultados = uc.execute(ListAppointmentsQuery(desde, hasta, profesional_id, estado))
    return [asdict(r) for r in resultados]


@router.get("/{turno_id}", response_model=TurnoResponse)
def obtener(turno_id: int, uc: GetAppointment = Depends(get_appointment_use_case)):
    return asdict(uc.execute(turno_id))


@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
def reservar(body: ReservarTurnoRequest, uc: BookAppointment = Depends(get_booking_use_case)):
    return asdict(uc.execute(BookAppointmentCommand(**body.model_dump())))


@router.post("/{turno_id}/cancelar", response_model=TurnoResponse)
def cancelar(turno_id: int, uc: CancelAppointment = Depends(get_cancel_appointment_use_case)):
    return asdict(uc.execute(turno_id))


@router.patch("/{turno_id}/estado", response_model=TurnoResponse)
def cambiar_estado(
    turno_id: int, body: CambiarEstadoRequest,
    uc: ChangeAppointmentStatus = Depends(get_change_status_use_case),
):
    return asdict(uc.execute(ChangeAppointmentStatusCommand(turno_id, body.nuevo_estado)))