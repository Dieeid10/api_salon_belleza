from app.modules.servicios.application.dto import (
    ActualizarServicioCommand,
    CrearServicioCommand,
    ServicioResult,
)
from app.modules.servicios.application.ports import ServicioRepository
from app.modules.servicios.domain.entities import Servicio
from app.modules.servicios.domain.errors import ServicioNoEncontrado


def _to_result(servicio: Servicio) -> ServicioResult:
    assert servicio.id is not None
    return ServicioResult(
        id=servicio.id,
        nombre_servicio=servicio.nombre_servicio,
        descripcion=servicio.descripcion,
        precio=servicio.precio,
        duracion_minutos=servicio.duracion_minutos,
        visible_online=servicio.visible_online,
        activo=servicio.activo,
    )


class ServiciosUseCases:
    def __init__(self, repo: ServicioRepository) -> None:
        self._repo = repo

    def crear(self, cmd: CrearServicioCommand) -> ServicioResult:
        servicio = Servicio(
            nombre_servicio=cmd.nombre_servicio,
            descripcion=cmd.descripcion,
            precio=cmd.precio,
            duracion_minutos=cmd.duracion_minutos,
            visible_online=cmd.visible_online,
        )
        return _to_result(self._repo.crear(servicio))

    def obtener(self, servicio_id: int) -> ServicioResult:
        return _to_result(self._get_or_fail(servicio_id))

    def obtener_publico(self, servicio_id: int) -> ServicioResult:
        servicio = self._get_or_fail(servicio_id)
        if not servicio.activo or not servicio.visible_online:
            raise ServicioNoEncontrado()
        return _to_result(servicio)

    def listar(
        self, solo_activos: bool = True, solo_visibles_online: bool = True
    ) -> list[ServicioResult]:
        return [
            _to_result(servicio)
            for servicio in self._repo.listar(solo_activos, solo_visibles_online)
        ]

    def actualizar(self, cmd: ActualizarServicioCommand) -> ServicioResult:
        servicio = self._get_or_fail(cmd.servicio_id)
        servicio.actualizar_datos(
            cmd.nombre_servicio,
            cmd.precio,
            cmd.duracion_minutos,
            cmd.descripcion,
            cmd.visible_online,
        )
        return _to_result(self._repo.actualizar(servicio))

    def desactivar(self, servicio_id: int) -> None:
        servicio = self._get_or_fail(servicio_id)
        servicio.desactivar()
        self._repo.actualizar(servicio)

    def _get_or_fail(self, servicio_id: int) -> Servicio:
        servicio = self._repo.obtener(servicio_id)
        if servicio is None:
            raise ServicioNoEncontrado()
        return servicio