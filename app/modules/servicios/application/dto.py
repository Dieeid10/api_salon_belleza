from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateServiceCommand:
    nombre_servicio: str
    precio: Decimal
    duracion_minutos: int = 60
    descripcion: str | None = None
    visible_online: bool = True


@dataclass(frozen=True)
class UpdateServiceCommand:
    servicio_id: int
    nombre_servicio: str
    precio: Decimal
    duracion_minutos: int = 60
    descripcion: str | None = None
    visible_online: bool = True


@dataclass(frozen=True)
class ServiceResult:
    id: int
    nombre_servicio: str
    descripcion: str | None
    precio: Decimal
    duracion_minutos: int
    visible_online: bool
    activo: bool


@dataclass(frozen=True)
class ServiceCatalogInfo:
    id: int
    nombre: str
    duracion_min: int
    precio: Decimal