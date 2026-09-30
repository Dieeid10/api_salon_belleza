from typing import Protocol

from app.modules.clientes.domain.entities import Cliente
from app.modules.descuentos.domain.entities import Descuento
from app.modules.turnos.application.dto import TurnoVentaInfo
from app.modules.ventas.domain.entities import Venta


class VentaRepository(Protocol):
    def crear(self, venta: Venta) -> Venta: ...
    def obtener(self, venta_id: int) -> Venta | None: ...
    def listar(self) -> list[Venta]: ...
    def obtener_por_turno(self, turno_id: int) -> Venta | None: ...


class TurnoVentaLookup(Protocol):
    def obtener_para_venta(
        self, turno_id: int, bloquear: bool = False
    ) -> TurnoVentaInfo | None: ...


class ClienteLookup(Protocol):
    def obtener(self, cliente_id: int) -> Cliente | None: ...


class DescuentoChismeLookup(Protocol):
    def obtener_chisme(self) -> Descuento | None: ...