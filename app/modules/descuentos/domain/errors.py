from app.shared.error import ConflictError, NotFoundError


class DescuentoNoEncontrado(NotFoundError):
    default_message = "El descuento no existe"


class DescuentoChismeYaConfigurado(ConflictError):
    default_message = "Ya existe la configuración del descuento por chisme"


class ServicioDescuentoNoEncontrado(NotFoundError):
    default_message = "El servicio asociado al descuento no existe"