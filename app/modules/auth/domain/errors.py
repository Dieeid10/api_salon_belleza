from app.shared.error import DomainError

class CredencialesInvalidas(DomainError):
    default_message = "Email o contraseña incorrectos"