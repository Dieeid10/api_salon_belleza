from app.shared.error import NotFoundError


class ClienteNoEncontrada(NotFoundError):
    default_message = "La clienta no existe"