from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class CreateProfessionalCommand:
    nombre: str
    perfil_id: str | None = None


@dataclass(frozen=True)
class UpdateProfessionalCommand:
    profesional_id: int
    nombre: str
    perfil_id: str | None = None


@dataclass(frozen=True)
class ProfessionalResult:
    id: int
    nombre: str
    perfil_id: str | None
    activo: bool


@dataclass(frozen=True)
class BusinessHoursInfo:
    hora_apertura: time
    hora_cierre: time