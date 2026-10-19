from app.modules.servicios.application.dto import (
    CreateServiceCommand,
    ServiceResult,
    UpdateServiceCommand,
)
from app.modules.servicios.application.ports import ServiceRepository
from app.modules.servicios.domain.entities import Service
from app.modules.servicios.domain.errors import ServiceNotFound


def _to_result(servicio: Service) -> ServiceResult:
    assert servicio.id is not None
    return ServiceResult(
        id=servicio.id,
        nombre_servicio=servicio.nombre_servicio,
        descripcion=servicio.descripcion,
        precio=servicio.precio,
        duracion_minutos=servicio.duracion_minutos,
        visible_online=servicio.visible_online,
        activo=servicio.activo,
    )


class ServiceUseCases:
    def __init__(self, repo: ServiceRepository) -> None:
        self._repo = repo

    def create(self, cmd: CreateServiceCommand) -> ServiceResult:
        servicio = Service(
            nombre_servicio=cmd.nombre_servicio,
            descripcion=cmd.descripcion,
            precio=cmd.precio,
            duracion_minutos=cmd.duracion_minutos,
            visible_online=cmd.visible_online,
        )
        return _to_result(self._repo.create(servicio))

    def get(self, servicio_id: int) -> ServiceResult:
        return _to_result(self._get_or_raise(servicio_id))

    def get_public(self, servicio_id: int) -> ServiceResult:
        servicio = self._get_or_raise(servicio_id)
        if not servicio.activo or not servicio.visible_online:
            raise ServiceNotFound()
        return _to_result(servicio)

    def list_all(
        self, active_only: bool = True, online_only: bool = True
    ) -> list[ServiceResult]:
        return [
            _to_result(servicio)
            for servicio in self._repo.list_all(active_only, online_only)
        ]

    def update(self, cmd: UpdateServiceCommand) -> ServiceResult:
        servicio = self._get_or_raise(cmd.servicio_id)
        servicio.update_details(
            cmd.nombre_servicio,
            cmd.precio,
            cmd.duracion_minutos,
            cmd.descripcion,
            cmd.visible_online,
        )
        return _to_result(self._repo.update(servicio))

    def deactivate(self, servicio_id: int) -> None:
        servicio = self._get_or_raise(servicio_id)
        servicio.deactivate()
        self._repo.update(servicio)

    def _get_or_raise(self, servicio_id: int) -> Service:
        servicio = self._repo.get(servicio_id)
        if servicio is None:
            raise ServiceNotFound()
        return servicio