from typing import Protocol

from app.modules.servicios.application.dto import ServicioCatalogoInfo
from app.modules.servicios.domain.entities import Servicio


class ServicioRepository(Protocol):
    def crear(self, servicio: Servicio) -> Servicio: pass
    def obtener(self, servicio_id: int) -> Servicio | None: pass
    def listar(
        self, solo_activos: bool = True, solo_visibles_online: bool = True
    ) -> list[Servicio]: pass
    def obtener_activos(self, servicio_ids: list[int]) -> list[ServicioCatalogoInfo]: pass
    def actualizar(self, servicio: Servicio) -> Servicio: pass