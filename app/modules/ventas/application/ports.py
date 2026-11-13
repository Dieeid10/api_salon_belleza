from typing import Protocol

from app.modules.ventas.application.dto import (
    GossipDiscountInfo,
    SaleAppointmentInfo,
)
from app.modules.ventas.domain.entities import Sale


class SaleRepository(Protocol):
    """Operaciones de almacenamiento que requieren los casos de uso de ventas."""

    def create(self, sale: Sale) -> Sale: ...
    def get(self, sale_id: int) -> Sale | None: ...
    def list_all(self) -> list[Sale]: ...
    def get_by_appointment(self, appointment_id: int) -> Sale | None: ...


class AppointmentSaleLookup(Protocol):
    """Consulta un turno cobrable sin exponer cómo se obtiene o persiste."""

    def get_for_sale(
        self, appointment_id: int, lock: bool = False
    ) -> SaleAppointmentInfo | None: ...


class ClientLookup(Protocol):
    """Comprueba la existencia de una clienta sin entregar su entidad a ventas."""

    def exists(self, client_id: int) -> bool: ...


class GossipDiscountLookup(Protocol):
    """Proporciona el descuento activo en el formato que ventas necesita."""

    def get_active_gossip_discount(self) -> GossipDiscountInfo | None: ...