from app.modules.turnos.application.dto import ServicioInfo
from app.modules.turnos.application.ports import TurnosUnitOfWork
from app.modules.turnos.domain.errors import (
    ProfesionalInexistente, ServicioInexistente, TurnoSinServicios,
)


def verificar_profesional(uow: TurnosUnitOfWork, profesional_id: int) -> None:
    if not uow.agenda.esta_activo(profesional_id):
        raise ProfesionalInexistente()


def cargar_servicios(uow: TurnosUnitOfWork, servicio_ids: list[int]) -> list[ServicioInfo]:
    ids = list(dict.fromkeys(servicio_ids))
    if not ids:
        raise TurnoSinServicios()
    servicios = uow.servicios.obtener_activos(ids)
    if len(servicios) != len(ids):
        raise ServicioInexistente()
    return servicios