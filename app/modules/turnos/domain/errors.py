from app.shared.error import ConflictError, NotFoundError, ValidationError

class TimeSlotUnavailable(ConflictError):
    default_message = "El horario elegido ya no está disponible"

class InvalidStatusTransition(ConflictError):
    default_message = "El cambio de estado no está permitido"

class AppointmentInPast(ValidationError):
    default_message = "No se puede reservar un turno en el pasado"

class AppointmentNotStarted(ValidationError):
    default_message = "El turno todavía no comenzó"

class AppointmentWithoutServices(ValidationError):
    default_message = "El turno necesita al menos un servicio"

class InvalidTimeSlot(ValidationError):
    default_message = "La franja horaria es inválida"

class AppointmentNotFound(NotFoundError):
    default_message = "El turno no existe"

class ProfessionalUnavailable(NotFoundError):
    default_message = "El profesional no existe o no está activo"

class ServiceUnavailable(NotFoundError):
    default_message = "Alguno de los servicios no existe o no está activo"