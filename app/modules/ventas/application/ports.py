from typing import Protocol

from app.modules.clientes.domain.entities import Client
from app.modules.descuentos.domain.entities import Discount
from app.modules.turnos.application.dto import AppointmentSaleInfo
from app.modules.ventas.domain.entities import Sale


class SaleRepository(Protocol):
    def create(self, sale: Sale) -> Sale: ...
    def get(self, sale_id: int) -> Sale | None: ...
    def list_all(self) -> list[Sale]: ...
    def get_by_appointment(self, appointment_id: int) -> Sale | None: ...


class AppointmentSaleLookup(Protocol):
    def get_for_sale(
        self, appointment_id: int, lock: bool = False
    ) -> AppointmentSaleInfo | None: ...


class ClientLookup(Protocol):
    def get(self, client_id: int) -> Client | None: ...


class GossipDiscountLookup(Protocol):
    def get_gossip_discount(self) -> Discount | None: ...