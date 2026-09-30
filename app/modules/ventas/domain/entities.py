from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from app.shared.error import ValidationError


_CENTAVO = Decimal("0.01")


def _validar_importe(nombre: str, importe: Decimal) -> Decimal:
    valor = Decimal(str(importe))
    if not valor.is_finite() or valor < 0:
        raise ValidationError(f"{nombre} debe ser un importe válido no negativo")
    if valor.as_tuple().exponent < -2:
        raise ValidationError(f"{nombre} admite como máximo dos decimales")
    return valor


@dataclass(frozen=True)
class DetalleVenta:
    servicio_id: int | None
    descuento_id: int | None
    precio_lista: Decimal | None
    descuento_pct: Decimal
    precio_cobrado: Decimal

    def __post_init__(self) -> None:
        if self.precio_lista is not None:
            object.__setattr__(
                self,
                "precio_lista",
                _validar_importe("El precio de lista", self.precio_lista),
            )
        object.__setattr__(
            self,
            "precio_cobrado",
            _validar_importe("El precio cobrado", self.precio_cobrado),
        )
        porcentaje = Decimal(str(self.descuento_pct))
        if not porcentaje.is_finite() or porcentaje < 0 or porcentaje > 100:
            raise ValidationError("El porcentaje aplicado debe estar entre 0 y 100")
        if porcentaje.as_tuple().exponent < -2:
            raise ValidationError("El porcentaje aplicado admite dos decimales")
        object.__setattr__(self, "descuento_pct", porcentaje)


@dataclass
class Venta:
    fecha_hora: datetime
    cliente_id: int | None
    empleado_id: UUID | None
    turno_id: int | None
    descuento_chisme_id: int | None
    chisme_pct: Decimal
    chisme_detalle: str | None
    detalles: list[DetalleVenta] = field(default_factory=list)
    id: int | None = None

    def __post_init__(self) -> None:
        if self.fecha_hora.tzinfo is None:
            raise ValidationError("La fecha de venta debe incluir zona horaria")
        if not self.detalles:
            raise ValidationError("La venta debe tener al menos un detalle")
        porcentaje = Decimal(str(self.chisme_pct))
        if not porcentaje.is_finite() or porcentaje < 0 or porcentaje > 100:
            raise ValidationError("El descuento por chisme debe estar entre 0 y 100")
        if porcentaje.as_tuple().exponent < -2:
            raise ValidationError("El descuento por chisme admite dos decimales")
        self.chisme_pct = porcentaje
        self.chisme_detalle = self.chisme_detalle.strip() if self.chisme_detalle else None
        if self.chisme_detalle is not None and len(self.chisme_detalle) > 250:
            raise ValidationError("El detalle del chisme no puede superar 250 caracteres")
        if self.chisme_pct == 0 and self.descuento_chisme_id is not None:
            raise ValidationError("No corresponde descuento de chisme con porcentaje cero")

    @property
    def subtotal(self) -> Decimal:
        return sum(
            (detalle.precio_cobrado for detalle in self.detalles), Decimal("0.00")
        ).quantize(_CENTAVO, rounding=ROUND_HALF_UP)

    @property
    def descuento_chisme(self) -> Decimal:
        return (self.subtotal * self.chisme_pct / Decimal("100")).quantize(
            _CENTAVO, rounding=ROUND_HALF_UP
        )

    @property
    def total(self) -> Decimal:
        return (self.subtotal - self.descuento_chisme).quantize(
            _CENTAVO, rounding=ROUND_HALF_UP
        )