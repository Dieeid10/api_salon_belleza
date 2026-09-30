# app/shared/domain/errors.py


class DomainError(Exception):
    """Base de todos los errores de dominio."""

    default_message = "Error de dominio"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(DomainError):
    """El recurso pedido no existe."""

    default_message = "Recurso no encontrado"


class ConflictError(DomainError):
    """La operación choca con el estado actual (ej: horario ocupado)."""

    default_message = "Conflicto con el estado actual"


class ValidationError(DomainError):
    """Una regla de negocio no se cumple (ej: turno en el pasado)."""

    default_message = "Datos inválidos"


class ForbiddenError(DomainError):
    """La operación no está permitida."""

    default_message = "Operación no permitida"