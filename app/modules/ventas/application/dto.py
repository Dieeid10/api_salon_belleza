from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class RegisterSaleCommand:
    """Datos que la API entrega al caso de uso para registrar una venta."""

    turno_id: int
    empleado_id: UUID
    chisme_detalle: str | None = None


@dataclass(frozen=True)
class GossipDiscountInfo:
    """Información mínima del descuento que ventas necesita aplicar."""

    id: int
    porcentaje: Decimal


@dataclass(frozen=True)
class SaleDetailResult:
    """Datos de un servicio tal como se guardaron dentro de la venta."""

    servicio_id: int | None
    descuento_id: int | None
    precio_lista: Decimal | None
    descuento_pct: Decimal
    precio_cobrado: Decimal


@dataclass(frozen=True)
class SaleResult:
    """Resultado de lectura o registro que se entrega a la capa HTTP."""

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
    detalles: list[SaleDetailResult]

@dataclass(frozen=True)
class SaleAppointmentDetailInfo:
    """Datos de cada servicio del turno necesarios para cobrarlo."""

    servicio_id: int
    descuento_id: int | None
    precio_lista: Decimal
    descuento_pct: Decimal
    precio_reservado: Decimal


@dataclass(frozen=True)
class SaleAppointmentInfo:
    """Vista del turno reducida a la información requerida por ventas."""

    id: int
    cliente_id: int
    is_completed: bool
    detalles: list[SaleAppointmentDetailInfo]