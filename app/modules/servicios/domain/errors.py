from app.shared.error import NotFoundError


class ServiceNotFound(NotFoundError):
    default_message = "El servicio no existe"