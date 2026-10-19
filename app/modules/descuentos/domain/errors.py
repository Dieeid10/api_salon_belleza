from app.shared.error import ConflictError, NotFoundError


class DiscountNotFound(NotFoundError):
    default_message = "El descuento no existe"


class GossipDiscountAlreadyConfigured(ConflictError):
    default_message = "Ya existe la configuración del descuento por chisme"


class DiscountServiceNotFound(NotFoundError):
    default_message = "El servicio asociado al descuento no existe"