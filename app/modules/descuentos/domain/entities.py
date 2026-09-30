from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum

from app.shared.error import ValidationError


class TipoDescuento(StrEnum):
    SERVICIO = "servicio"
    CHISME = "chisme"


@dataclass
class Descuento:
    nombre: str
    tipo: TipoDescuento
    porcentaje: Decimal
    servicio_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activo: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()
        self.tipo = TipoDescuento(self.tipo)
        self.porcentaje = Decimal(str(self.porcentaje))

        if not self.nombre:
            raise ValidationError("El nombre del descuento es obligatorio")
        if len(self.nombre) > 100:
            raise ValidationError("El nombre del descuento no puede superar 100 caracteres")
        if not self.porcentaje.is_finite():
            raise ValidationError("El porcentaje debe ser un número finito")
        if self.porcentaje <= 0 or self.porcentaje > 100:
            raise ValidationError("El porcentaje debe ser mayor a 0 y menor o igual a 100")
        if self.porcentaje.as_tuple().exponent < -2:
            raise ValidationError("El porcentaje admite como máximo dos decimales")
        if self.tipo is TipoDescuento.SERVICIO and self.servicio_id is None:
            raise ValidationError("El descuento de servicio debe indicar un servicio")
        if self.tipo is TipoDescuento.CHISME and self.servicio_id is not None:
            raise ValidationError("El descuento por chisme no puede asociarse a un servicio")
        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValidationError("La fecha final no puede ser anterior a la inicial")

    def vigente_en(self, fecha: date) -> bool:
        return (
            self.activo
            and (self.fecha_inicio is None or self.fecha_inicio <= fecha)
            and (self.fecha_fin is None or self.fecha_fin >= fecha)
        )

    def calcular_precio(self, precio: Decimal, fecha: date) -> Decimal:
        if not precio.is_finite():
            raise ValidationError("El precio debe ser un número finito")
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo")
        if not self.vigente_en(fecha):
            return precio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        factor = Decimal("1") - self.porcentaje / Decimal("100")
        return (precio * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def actualizar_datos(
        self,
        nombre: str,
        tipo: TipoDescuento,
        porcentaje: Decimal,
        servicio_id: int | None,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> None:
        actualizado = Descuento(
            nombre=nombre,
            tipo=tipo,
            porcentaje=porcentaje,
            servicio_id=servicio_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activo=self.activo,
            id=self.id,
        )
        self.nombre = actualizado.nombre
        self.tipo = actualizado.tipo
        self.porcentaje = actualizado.porcentaje
        self.servicio_id = actualizado.servicio_id
        self.fecha_inicio = actualizado.fecha_inicio
        self.fecha_fin = actualizado.fecha_fin

    def desactivar(self) -> None:
        self.activo = False