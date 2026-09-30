from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CrearClienteCommand:
    nombre: str
    apellido: str
    telefono: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class ActualizarClienteCommand:
    cliente_id: int
    nombre: str
    apellido: str
    telefono: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class ClienteResult:
    id: int
    nombre: str
    apellido: str
    telefono: str | None
    email: str | None
    activo: bool
    fecha_creacion: datetime