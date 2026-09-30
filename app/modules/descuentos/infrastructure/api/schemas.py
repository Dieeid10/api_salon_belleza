from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.modules.descuentos.domain.entities import TipoDescuento


class DescuentoRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    tipo: TipoDescuento
    porcentaje: Decimal = Field(gt=0, le=100, max_digits=5, decimal_places=2)
    servicio_id: int | None = Field(default=None, gt=0)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class DescuentoResponse(BaseModel):
    id: int
    nombre: str
    tipo: TipoDescuento
    porcentaje: Decimal
    servicio_id: int | None
    fecha_inicio: date | None
    fecha_fin: date | None
    activo: bool