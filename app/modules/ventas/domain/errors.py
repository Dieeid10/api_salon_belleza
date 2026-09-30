from app.shared.error import ConflictError, NotFoundError, ValidationError


class VentaNoEncontrada(NotFoundError):
    default_message = "La venta no existe"


class TurnoVentaNoEncontrado(NotFoundError):
    default_message = "El turno asociado a la venta no existe"


class TurnoNoRealizado(ValidationError):
    default_message = "Solo se puede registrar una venta para un turno realizado"


class VentaDeTurnoDuplicada(ConflictError):
    default_message = "Ya existe una venta para ese turno"


class DescuentoChismeNoDisponible(ValidationError):
    default_message = "El descuento por chisme no está disponible"