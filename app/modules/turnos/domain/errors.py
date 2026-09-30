from app.shared.error import ConflictError, NotFoundError, ValidationError

class HorarioNoDisponible(ConflictError):
    default_message = "El horario elegido ya no está disponible"

class TransicionInvalida(ConflictError):
    default_message = "El cambio de estado no está permitido"

class TurnoEnElPasado(ValidationError):
    default_message = "No se puede reservar un turno en el pasado"

class TurnoNoIniciado(ValidationError):
    default_message = "El turno todavía no comenzó"

class TurnoSinServicios(ValidationError):
    default_message = "El turno necesita al menos un servicio"

class FranjaInvalida(ValidationError):
    default_message = "La franja horaria es inválida"

class TurnoNoEncontrado(NotFoundError):
    default_message = "El turno no existe"

class ProfesionalInexistente(NotFoundError):
    default_message = "El profesional no existe o no está activo"

class ServicioInexistente(NotFoundError):
    default_message = "Alguno de los servicios no existe o no está activo"