from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.modules.descuentos.domain.entities import TipoDescuento


@dataclass(frozen=True)
class CreateDiscountCommand:
    nombre: str
    tipo: TipoDescuento
    porcentaje: Decimal
    servicio_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


@dataclass(frozen=True)
class UpdateDiscountCommand:
    descuento_id: int
    nombre: str
    tipo: TipoDescuento
    porcentaje: Decimal
    servicio_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


@dataclass(frozen=True)
class DiscountResult:
    id: int
    nombre: str
    tipo: TipoDescuento
    porcentaje: Decimal
    servicio_id: int | None
    fecha_inicio: date | None
    fecha_fin: date | None
    activo: bool