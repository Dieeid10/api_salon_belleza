from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import Depends

from app.modules.turnos.application.use_cases.change_appointment_status import ChangeAppointmentStatus
from app.modules.turnos.application.use_cases.cancel_appointment import CancelAppointment
from app.modules.turnos.application.use_cases.check_appointment_availability import CheckAppointmentAvailability
from app.modules.turnos.application.use_cases.list_appointments import ListAppointments
from app.modules.turnos.application.use_cases.get_appointment import GetAppointment
from app.modules.turnos.application.use_cases.book_appointment import BookAppointment
from app.modules.turnos.infrastructure.persistence.unit_of_work import PsycopgAppointmentsUnitOfWork
from app.shared.infrastructure.config import settings

TIMEZONE = ZoneInfo(settings.zona_horaria)


def clock() -> datetime:
    return datetime.now(timezone.utc)


def get_unit_of_work() -> PsycopgAppointmentsUnitOfWork:
    return PsycopgAppointmentsUnitOfWork(TIMEZONE)


def get_availability_use_case(uow=Depends(get_unit_of_work)) -> CheckAppointmentAvailability:
    return CheckAppointmentAvailability(uow, clock)

def get_booking_use_case(uow=Depends(get_unit_of_work)) -> BookAppointment:
    return BookAppointment(uow, TIMEZONE, clock)

def get_cancel_appointment_use_case(uow=Depends(get_unit_of_work)) -> CancelAppointment:
    return CancelAppointment(uow, clock)

def get_change_status_use_case(uow=Depends(get_unit_of_work)) -> ChangeAppointmentStatus:
    return ChangeAppointmentStatus(uow, clock)

def get_appointment_use_case(uow=Depends(get_unit_of_work)) -> GetAppointment:
    return GetAppointment(uow)

def get_list_appointments_use_case(uow=Depends(get_unit_of_work)) -> ListAppointments:
    return ListAppointments(uow, TIMEZONE)