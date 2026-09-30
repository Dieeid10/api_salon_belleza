from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from app.modules.turnos.domain.errors import FranjaInvalida

class EstadoTurno(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    AUSENTE = "ausente"

    def puede_pasar_a(self, nuevo: "EstadoTurno") -> bool:
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
ESTADOS_ACTIVOS = (EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO)

@dataclass(frozen=True)
class FranjaHoraria:
    inicio: datetime
    fin: datetime

    def __post_init__(self) -> None:
        if self.inicio.tzinfo is None or self.fin.tzinfo is None:
            raise FranjaInvalida("Las fechas deben incluir zona horaria")
        if self.fin <= self.inicio:
            raise FranjaInvalida("El fin debe ser posterior al inicio")

    @property
    def duracion(self) -> timedelta:
        return self.fin - self.inicio

    def solapa(self, otra: "FranjaHoraria") -> bool:
        return self.inicio < otra.fin and otra.inicio < self.fin

    def contiene(self, otra: "FranjaHoraria") -> bool:
        return self.inicio <= otra.inicio and otra.fin <= self.fin