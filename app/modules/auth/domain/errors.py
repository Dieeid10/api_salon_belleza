from app.shared.error import DomainError

class InvalidCredentials(DomainError):
    default_message = "Email o contraseña incorrectos"