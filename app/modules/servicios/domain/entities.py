from dataclasses import dataclass
from decimal import Decimal

from app.shared.error import ValidationError


@dataclass
class Servicio:
    nombre_servicio: str
    precio: Decimal
    duracion_minutos: int = 60
    descripcion: str | None = None
    visible_online: bool = True
    activo: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        self.nombre_servicio = self.nombre_servicio.strip()
        self.descripcion = self.descripcion.strip() if self.descripcion else None
        self.precio = Decimal(str(self.precio))

        if not self.nombre_servicio:
            raise ValidationError("El nombre del servicio es obligatorio")
        if len(self.nombre_servicio) > 100:
            raise ValidationError("El nombre del servicio no puede superar 100 caracteres")
        if self.descripcion is not None and len(self.descripcion) > 255:
            raise ValidationError("La descripción no puede superar 255 caracteres")
        if self.precio < 0:
            raise ValidationError("El precio no puede ser negativo")
        if self.precio.as_tuple().exponent < -2:
            raise ValidationError("El precio admite como máximo dos decimales")
        if self.precio >= Decimal("100000000"):
            raise ValidationError("El precio supera el máximo permitido")
        if self.duracion_minutos <= 0:
            raise ValidationError("La duración debe ser mayor a cero")

    def actualizar_datos(
        self,
        nombre_servicio: str,
        precio: Decimal,
        duracion_minutos: int,
        descripcion: str | None,
        visible_online: bool,
    ) -> None:
        actualizado = Servicio(
            nombre_servicio=nombre_servicio,
            precio=precio,
            duracion_minutos=duracion_minutos,
            descripcion=descripcion,
            visible_online=visible_online,
            activo=self.activo,
            id=self.id,
        )
        self.nombre_servicio = actualizado.nombre_servicio
        self.precio = actualizado.precio
        self.duracion_minutos = actualizado.duracion_minutos
        self.descripcion = actualizado.descripcion
        self.visible_online = actualizado.visible_online

    def desactivar(self) -> None:
        self.activo = False