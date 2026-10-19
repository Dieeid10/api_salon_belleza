from app.shared.error import NotFoundError


class ProfessionalNotFound(NotFoundError):
    default_message = "El profesional no existe"