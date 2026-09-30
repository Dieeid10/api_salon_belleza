from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CrearServicioCommand:
    nombre_servicio: str
    precio: Decimal
    duracion_minutos: int = 60
    descripcion: str | None = None
    visible_online: bool = True


@dataclass(frozen=True)
class ActualizarServicioCommand:
    servicio_id: int
    nombre_servicio: str
    precio: Decimal
    duracion_minutos: int = 60
    descripcion: str | None = None
    visible_online: bool = True


@dataclass(frozen=True)
class ServicioResult:
    id: int
    nombre_servicio: str
    descripcion: str | None
    precio: Decimal
    duracion_minutos: int
    visible_online: bool
    activo: bool


@dataclass(frozen=True)
class ServicioCatalogoInfo:
    id: int
    nombre: str
    duracion_min: int
    precio: Decimal