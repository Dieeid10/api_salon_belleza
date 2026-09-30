from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from app.modules.turnos.domain.value_objects import EstadoTurno


@dataclass(frozen=True)
class ServicioInfo:
    """Lo que turnos necesita saber de un servicio."""
    id: int
    nombre: str
    duracion_min: int
    precio: Decimal


@dataclass(frozen=True)
class DetalleTurnoVentaInfo:
    servicio_id: int
    descuento_id: int | None
    precio_lista: Decimal
    descuento_pct: Decimal
    precio_reservado: Decimal


@dataclass(frozen=True)
class TurnoVentaInfo:
    id: int
    cliente_id: int
    estado: str
    detalles: list[DetalleTurnoVentaInfo]


@dataclass(frozen=True)
class ConsultarDisponibilidadQuery:
    profesional_id: int
    servicio_ids: list[int]
    fecha: date


@dataclass(frozen=True)
class ReservarTurnoCommand:
    nombre: str
    apellido: str
    telefono: str
    profesional_id: int
    servicio_ids: list[int]
    inicio: datetime


@dataclass(frozen=True)
class CambiarEstadoCommand:
    turno_id: int
    nuevo_estado: EstadoTurno


@dataclass(frozen=True)
class ListarTurnosQuery:
    desde: date
    hasta: date
    profesional_id: int | None = None
    estado: EstadoTurno | None = None


@dataclass(frozen=True)
class DetalleResult:
    servicio_id: int
    nombre: str
    duracion_min: int
    precio: Decimal


@dataclass(frozen=True)
class TurnoResult:
    id: int
    cliente_id: int
    profesional_id: int
    inicio: datetime
    fin: datetime
    estado: str
    total: Decimal
    detalles: list[DetalleResult]


@dataclass(frozen=True)
class DisponibilidadResult:
    profesional_id: int
    fecha: date
    duracion_min: int
    horarios: list[datetime]