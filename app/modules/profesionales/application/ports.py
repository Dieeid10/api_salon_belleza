from datetime import date
from typing import Protocol

from app.modules.profesionales.application.dto import HorarioAtencionInfo
from app.modules.profesionales.domain.entities import Profesional


class ProfesionalRepository(Protocol):
    def crear(self, profesional: Profesional) -> Profesional: pass
    def obtener(self, profesional_id: int) -> Profesional | None: pass
    def listar(self, solo_activos: bool = True) -> list[Profesional]: pass
    def actualizar(self, profesional: Profesional) -> Profesional: pass
    def esta_activo(self, profesional_id: int) -> bool: pass


class HorarioAtencionRepository(Protocol):
    def jornada(self, profesional_id: int, fecha: date) -> list[HorarioAtencionInfo]: pass