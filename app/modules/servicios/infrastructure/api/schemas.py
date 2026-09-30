from decimal import Decimal

from pydantic import BaseModel, Field


class ServicioRequest(BaseModel):
    nombre_servicio: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)
    precio: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    duracion_minutos: int = Field(default=60, gt=0)
    visible_online: bool = True


class ServicioResponse(BaseModel):
    id: int
    nombre_servicio: str
    descripcion: str | None
    precio: Decimal
    duracion_minutos: int
    visible_online: bool
    activo: bool