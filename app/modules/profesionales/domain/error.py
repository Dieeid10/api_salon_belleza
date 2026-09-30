from app.shared.error import NotFoundError


class ProfesionalNoEncontrado(NotFoundError):
    default_message = "El profesional no existe"