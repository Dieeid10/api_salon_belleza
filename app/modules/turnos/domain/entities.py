from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.turnos.domain.errors import (
    AppointmentInPast, AppointmentNotStarted, AppointmentWithoutServices,
    InvalidStatusTransition,
)
from app.modules.turnos.domain.value_objects import EstadoTurno, TimeSlot
from app.shared.error import ValidationError

@dataclass(frozen=True)
class DetalleTurno:
    servicio_id: int
    nombre: str
    duracion_min: int
    precio: Decimal

@dataclass
class Turno:
    cliente_id: int
    profesional_id: int
    franja: TimeSlot
    detalles: list[DetalleTurno]
    estado: EstadoTurno = EstadoTurno.PENDIENTE
    id: int | None = None

    @property
    def total(self) -> Decimal:
        return sum((d.precio for d in self.detalles), Decimal(0))

    @classmethod
    def schedule(cls, cliente_id: int, profesional_id: int, inicio: datetime, detalles: list[DetalleTurno], ahora: datetime) -> "Turno":
        if not detalles:
            raise AppointmentWithoutServices()

        if inicio.tzinfo is None:
            raise ValidationError("El inicio debe incluir zona horaria")

        if inicio <= ahora:
            raise AppointmentInPast()

        duracion = timedelta(minutes=sum(d.duracion_min for d in detalles))
            
        return cls(
            cliente_id=cliente_id,
            profesional_id=profesional_id,
            franja=TimeSlot(inicio, inicio + duracion),
            detalles=list(detalles),
        )

    def change_status(self, nuevo: EstadoTurno, ahora: datetime) -> None:
        if not self.estado.can_transition_to(nuevo):
            raise InvalidStatusTransition(
                f"No se puede pasar de '{self.estado.value}' a '{nuevo.value}'"
            )

        if nuevo in (EstadoTurno.COMPLETADO, EstadoTurno.AUSENTE) and ahora < self.franja.inicio:
            raise AppointmentNotStarted()
            
        self.estado = nuevo

    def cancel(self, ahora: datetime) -> None:
        self.change_status(EstadoTurno.CANCELADO, ahora)