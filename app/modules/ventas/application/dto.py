from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class RegistrarVentaCommand:
    turno_id: int
    empleado_id: UUID
    chisme_detalle: str | None = None


@dataclass(frozen=True)
class DetalleVentaResult:
    servicio_id: int | None
    descuento_id: int | None
    precio_lista: Decimal | None
    descuento_pct: Decimal
    precio_cobrado: Decimal


@dataclass(frozen=True)
class VentaResult:
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
    detalles: list[DetalleVentaResult]