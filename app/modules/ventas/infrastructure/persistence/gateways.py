from app.modules.clientes.infrastructure.persistence.client_repository import (
    PsycopgClientRepository,
)
from app.modules.descuentos.infrastructure.persistence.discount_repository import (
    PsycopgDiscountRepository,
)
from app.modules.turnos.infrastructure.persistence.appointment_repository import (
    PsycopgAppointmentRepository,
)
from app.modules.ventas.application.dto import (
    GossipDiscountInfo,
    SaleAppointmentDetailInfo,
    SaleAppointmentInfo,
)


class PsycopgClientLookup:
    """Adapta el repositorio de clientes a la consulta de existencia de ventas."""

    def __init__(self, repository: PsycopgClientRepository) -> None:
        self._repository = repository

    def exists(self, client_id: int) -> bool:
        return self._repository.get(client_id) is not None


class PsycopgGossipDiscountLookup:
    """Traduce el descuento de descuentos al dato mínimo que requiere ventas."""

    def __init__(self, repository: PsycopgDiscountRepository) -> None:
        self._repository = repository

    def get_active_gossip_discount(self) -> GossipDiscountInfo | None:
        discount = self._repository.get_gossip_discount()
        if discount is None or not discount.activo or discount.id is None:
            return None
        return GossipDiscountInfo(
            id=discount.id,
            porcentaje=discount.porcentaje,
        )


class PsycopgAppointmentSaleLookup:
    """Adapta la consulta de turnos al contrato de aplicación de ventas."""

    def __init__(self, repository: PsycopgAppointmentRepository) -> None:
        self._repository = repository

    def get_for_sale(
        self, appointment_id: int, lock: bool = False
    ) -> SaleAppointmentInfo | None:
        """Convierte el estado y los detalles del turno a DTOs propios de ventas."""
        appointment = self._repository.get_for_sale(appointment_id, lock)
        if appointment is None:
            return None
        return SaleAppointmentInfo(
            id=appointment.id,
            cliente_id=appointment.cliente_id,
            is_completed=appointment.estado == "Realizado",
            detalles=[
                SaleAppointmentDetailInfo(
                    servicio_id=detail.servicio_id,
                    descuento_id=detail.descuento_id,
                    precio_lista=detail.precio_lista,
                    descuento_pct=detail.descuento_pct,
                    precio_reservado=detail.precio_reservado,
                )
                for detail in appointment.detalles
            ],
        )