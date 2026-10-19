from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from app.modules.turnos.domain.errors import InvalidTimeSlot

class EstadoTurno(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    AUSENTE = "ausente"

    def can_transition_to(self, nuevo: "EstadoTurno") -> bool:
        return nuevo in _TRANSICIONES[self]


_TRANSICIONES: dict[EstadoTurno, set[EstadoTurno]] = {
    EstadoTurno.PENDIENTE: {EstadoTurno.CONFIRMADO, EstadoTurno.CANCELADO},
    EstadoTurno.CONFIRMADO: {
        EstadoTurno.COMPLETADO, EstadoTurno.CANCELADO, EstadoTurno.AUSENTE,
    },
    EstadoTurno.COMPLETADO: set(),
    EstadoTurno.CANCELADO: set(),
    EstadoTurno.AUSENTE: set(),
}

# Los estados que bloquean la agenda del profesional
ACTIVE_STATES = (EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO)

@dataclass(frozen=True)
class TimeSlot:
    inicio: datetime
    fin: datetime

    def __post_init__(self) -> None:
        if self.inicio.tzinfo is None or self.fin.tzinfo is None:
            raise InvalidTimeSlot("Las fechas deben incluir zona horaria")
        if self.fin <= self.inicio:
            raise InvalidTimeSlot("El fin debe ser posterior al inicio")

    @property
    def duracion(self) -> timedelta:
        return self.fin - self.inicio

    def overlaps(self, otra: "TimeSlot") -> bool:
        return self.inicio < otra.fin and otra.inicio < self.fin

    def contains(self, otra: "TimeSlot") -> bool:
        return self.inicio <= otra.inicio and otra.fin <= self.fin