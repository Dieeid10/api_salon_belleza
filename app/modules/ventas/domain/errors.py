from app.shared.error import ConflictError, NotFoundError, ValidationError


class SaleNotFound(NotFoundError):
    """La venta solicitada no existe."""

    default_message = "La venta no existe"


class SaleClientNotFound(NotFoundError):
    """El cliente asociado al turno ya no existe."""

    default_message = "La clienta no existe"


class AppointmentForSaleNotFound(NotFoundError):
    """No existe el turno que se quiere cobrar."""

    default_message = "El turno asociado a la venta no existe"


class AppointmentNotCompleted(ValidationError):
    """El turno no cumple las condiciones para registrar un cobro."""

    default_message = "Solo se puede registrar una venta para un turno realizado"


class DuplicateAppointmentSale(ConflictError):
    """El turno ya tiene una venta registrada."""

    default_message = "Ya existe una venta para ese turno"


class GossipDiscountUnavailable(ValidationError):
    """Se solicitó el descuento especial, pero no está disponible."""

    default_message = "El descuento por chisme no está disponible"