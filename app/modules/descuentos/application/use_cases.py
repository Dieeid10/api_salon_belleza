from datetime import date

from app.modules.descuentos.application.dto import (
    ActualizarDescuentoCommand,
    CrearDescuentoCommand,
    DescuentoResult,
)
from app.modules.descuentos.application.ports import DescuentoRepository, ServicioLookup
from app.modules.descuentos.domain.entities import Descuento, TipoDescuento
from app.modules.descuentos.domain.errors import (
    DescuentoNoEncontrado,
    ServicioDescuentoNoEncontrado,
)


def _to_result(descuento: Descuento) -> DescuentoResult:
    assert descuento.id is not None
    return DescuentoResult(
        id=descuento.id,
        nombre=descuento.nombre,
        tipo=descuento.tipo,
        porcentaje=descuento.porcentaje,
        servicio_id=descuento.servicio_id,
        fecha_inicio=descuento.fecha_inicio,
        fecha_fin=descuento.fecha_fin,
        activo=descuento.activo,
    )


class DescuentosUseCases:
    def __init__(
        self,
        repo: DescuentoRepository,
        servicios: ServicioLookup,
    ) -> None:
        self._repo = repo
        self._servicios = servicios

    def crear(self, cmd: CrearDescuentoCommand) -> DescuentoResult:
        self._validar_servicio(cmd.tipo, cmd.servicio_id)
        descuento = Descuento(
            nombre=cmd.nombre,
            tipo=cmd.tipo,
            porcentaje=cmd.porcentaje,
            servicio_id=cmd.servicio_id,
            fecha_inicio=cmd.fecha_inicio,
            fecha_fin=cmd.fecha_fin,
        )
        return _to_result(self._repo.crear(descuento))

    def obtener(self, descuento_id: int) -> DescuentoResult:
        return _to_result(self._get_or_fail(descuento_id))

    def listar(self) -> list[DescuentoResult]:
        return [_to_result(descuento) for descuento in self._repo.listar()]

    def listar_publicos(self, fecha: date) -> list[DescuentoResult]:
        return [
            _to_result(descuento)
            for descuento in self._repo.listar_publicos(fecha)
            if descuento.vigente_en(fecha)
            and descuento.servicio_id is not None
            and (servicio := self._servicios.obtener(descuento.servicio_id)) is not None
            and servicio.activo
            and servicio.visible_online
        ]

    def actualizar(self, cmd: ActualizarDescuentoCommand) -> DescuentoResult:
        self._validar_servicio(cmd.tipo, cmd.servicio_id)
        descuento = self._get_or_fail(cmd.descuento_id)
        descuento.actualizar_datos(
            cmd.nombre,
            cmd.tipo,
            cmd.porcentaje,
            cmd.servicio_id,
            cmd.fecha_inicio,
            cmd.fecha_fin,
        )
        return _to_result(self._repo.actualizar(descuento))

    def desactivar(self, descuento_id: int) -> None:
        descuento = self._get_or_fail(descuento_id)
        descuento.desactivar()
        self._repo.actualizar(descuento)

    def _get_or_fail(self, descuento_id: int) -> Descuento:
        descuento = self._repo.obtener(descuento_id)
        if descuento is None:
            raise DescuentoNoEncontrado()
        return descuento

    def _validar_servicio(
        self, tipo: TipoDescuento, servicio_id: int | None
    ) -> None:
        if tipo is TipoDescuento.SERVICIO:
            if servicio_id is None or self._servicios.obtener(servicio_id) is None:
                raise ServicioDescuentoNoEncontrado()