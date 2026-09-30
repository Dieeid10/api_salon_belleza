from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class RegistrarVentaRequest(BaseModel):
    turno_id: int = Field(gt=0)
    chisme_detalle: str | None = Field(default=None, max_length=250)


class DetalleVentaResponse(BaseModel):
    servicio_id: int | None
    descuento_id: int | None
    precio_lista: Decimal | None
    descuento_pct: Decimal
    precio_cobrado: Decimal


class VentaResponse(BaseModel):
    id: int
    fecha_hora: datetime
    cliente_id: int | None
    empleado_id: UUID | None
    turno_id: int | None
    descuento_chisme_id: int | None
    chisme_pct: Decimal
    chisme_detalle: str | None
    subtotal: Decimal
    descuento_chisme: Decimal
    total: Decimal
    detalles: list[DetalleVentaResponse]