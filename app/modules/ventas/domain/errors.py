from app.shared.error import ConflictError, NotFoundError, ValidationError


class SaleNotFound(NotFoundError):
    default_message = "La venta no existe"


class AppointmentForSaleNotFound(NotFoundError):
    default_message = "El turno asociado a la venta no existe"


class AppointmentNotCompleted(ValidationError):
    default_message = "Solo se puede registrar una venta para un turno realizado"


class DuplicateAppointmentSale(ConflictError):
    default_message = "Ya existe una venta para ese turno"


class GossipDiscountUnavailable(ValidationError):
    default_message = "El descuento por chisme no está disponible"