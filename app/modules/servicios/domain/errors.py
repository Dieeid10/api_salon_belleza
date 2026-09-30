from app.shared.error import NotFoundError


class ServicioNoEncontrado(NotFoundError):
    default_message = "El servicio no existe"