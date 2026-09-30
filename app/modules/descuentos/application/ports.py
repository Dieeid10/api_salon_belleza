from datetime import date
from typing import Protocol

from app.modules.descuentos.domain.entities import Descuento
from app.modules.servicios.domain.entities import Servicio


class DescuentoRepository(Protocol):
    def crear(self, descuento: Descuento) -> Descuento: pass
    def obtener(self, descuento_id: int) -> Descuento | None: pass
    def listar(self) -> list[Descuento]: pass
    def listar_publicos(self, fecha: date) -> list[Descuento]: pass
    def obtener_chisme(self) -> Descuento | None: pass
    def actualizar(self, descuento: Descuento) -> Descuento: pass


class ServicioLookup(Protocol):
    def obtener(self, servicio_id: int) -> Servicio | None: pass