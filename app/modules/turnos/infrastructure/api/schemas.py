from datetime import date, datetime
from decimal import Decimal

from pydantic import AwareDatetime, BaseModel, Field

from app.modules.turnos.domain.value_objects import EstadoTurno


class ReservarTurnoRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    telefono: str = Field(pattern=r"^\+?\d{8,15}$")
    profesional_id: int
    servicio_ids: list[int] = Field(min_length=1)
    inicio: AwareDatetime  # exige zona horaria, ej: 2026-10-05T15:00:00-03:00


class CambiarEstadoRequest(BaseModel):
    nuevo_estado: EstadoTurno


class DetalleResponse(BaseModel):
    servicio_id: int
    nombre: str
    duracion_min: int
    precio: Decimal


class TurnoPublicoResponse(BaseModel):
    """Lo que ve la invitada: sin ids internos de cliente."""
    id: int
    profesional_id: int
    inicio: datetime
    fin: datetime
    estado: str
    total: Decimal
    detalles: list[DetalleResponse]


class TurnoResponse(TurnoPublicoResponse):
    cliente_id: int


class DisponibilidadResponse(BaseModel):
    profesional_id: int
    fecha: date
    duracion_min: int
    horarios: list[datetime]