from app.shared.error import NotFoundError


class ClientNotFound(NotFoundError):
    default_message = "La clienta no existe"