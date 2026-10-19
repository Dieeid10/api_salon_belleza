from datetime import datetime, timedelta
from app.modules.turnos.domain.value_objects import TimeSlot

PASO_DEFAULT = timedelta(minutes=15)

def is_available(
    candidate: TimeSlot,
    schedule: list[TimeSlot],
    occupied: list[TimeSlot],
) -> bool:
    """La franja entra completa en la jornada y no pisa ningún turno activo."""
    within_schedule = any(slot.contains(candidate) for slot in schedule)
    return within_schedule and not any(candidate.overlaps(slot) for slot in occupied)

def calculate_slots(
    schedule: list[TimeSlot],
    occupied: list[TimeSlot],
    duration: timedelta,
    now: datetime,
    step: timedelta = PASO_DEFAULT,
) -> list[datetime]:
    """Horarios de inicio posibles para un turno de `duracion`."""
    slots: list[datetime] = []
    for time_slot in schedule:
        start = time_slot.inicio
        while start + duration <= time_slot.fin:
            candidate = TimeSlot(start, start + duration)
            if start > now and not any(candidate.overlaps(slot) for slot in occupied):
                slots.append(start)
            start += step
    return slots