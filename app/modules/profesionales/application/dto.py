from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class CrearProfesionalCommand:
    nombre: str
    perfil_id: str | None = None


@dataclass(frozen=True)
class ActualizarProfesionalCommand:
    profesional_id: int
    nombre: str
    perfil_id: str | None = None


@dataclass(frozen=True)
class ProfesionalResult:
    id: int
    nombre: str
    perfil_id: str | None
    activo: bool


@dataclass(frozen=True)
class HorarioAtencionInfo:
    hora_apertura: time
    hora_cierre: time