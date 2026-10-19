from datetime import date

from app.modules.descuentos.application.dto import (
    CreateDiscountCommand,
    DiscountResult,
    UpdateDiscountCommand,
)
from app.modules.descuentos.application.ports import DiscountRepository, ServiceLookup
from app.modules.descuentos.domain.entities import Discount, TipoDescuento
from app.modules.descuentos.domain.errors import (
    DiscountNotFound,
    DiscountServiceNotFound,
)


def _to_result(descuento: Discount) -> DiscountResult:
    assert descuento.id is not None
    return DiscountResult(
        id=descuento.id,
        nombre=descuento.nombre,
        tipo=descuento.tipo,
        porcentaje=descuento.porcentaje,
        servicio_id=descuento.servicio_id,
        fecha_inicio=descuento.fecha_inicio,
        fecha_fin=descuento.fecha_fin,
        activo=descuento.activo,
    )


class DiscountUseCases:
    def __init__(
        self,
        repo: DiscountRepository,
        servicios: ServiceLookup,
    ) -> None:
        self._repo = repo
        self._servicios = servicios

    def create(self, cmd: CreateDiscountCommand) -> DiscountResult:
        self._validar_servicio(cmd.tipo, cmd.servicio_id)
        descuento = Discount(
            nombre=cmd.nombre,
            tipo=cmd.tipo,
            porcentaje=cmd.porcentaje,
            servicio_id=cmd.servicio_id,
            fecha_inicio=cmd.fecha_inicio,
            fecha_fin=cmd.fecha_fin,
        )
        return _to_result(self._repo.create(descuento))

    def get(self, descuento_id: int) -> DiscountResult:
        return _to_result(self._get_or_raise(descuento_id))

    def list_all(self) -> list[DiscountResult]:
        return [_to_result(descuento) for descuento in self._repo.list_all()]

    def list_public(self, fecha: date) -> list[DiscountResult]:
        return [
            _to_result(descuento)
            for descuento in self._repo.list_public(fecha)
            if descuento.is_valid_on(fecha)
            and descuento.servicio_id is not None
            and (servicio := self._servicios.get(descuento.servicio_id)) is not None
            and servicio.activo
            and servicio.visible_online
        ]

    def update(self, cmd: UpdateDiscountCommand) -> DiscountResult:
        self._validar_servicio(cmd.tipo, cmd.servicio_id)
        descuento = self._get_or_raise(cmd.descuento_id)
        descuento.update_details(
            cmd.nombre,
            cmd.tipo,
            cmd.porcentaje,
            cmd.servicio_id,
            cmd.fecha_inicio,
            cmd.fecha_fin,
        )
        return _to_result(self._repo.update(descuento))

    def deactivate(self, descuento_id: int) -> None:
        descuento = self._get_or_raise(descuento_id)
        descuento.deactivate()
        self._repo.update(descuento)

    def _get_or_raise(self, descuento_id: int) -> Discount:
        descuento = self._repo.get(descuento_id)
        if descuento is None:
            raise DiscountNotFound()
        return descuento

    def _validar_servicio(
        self, tipo: TipoDescuento, servicio_id: int | None
    ) -> None:
        if tipo is TipoDescuento.SERVICIO:
            if servicio_id is None or self._servicios.get(servicio_id) is None:
                raise DiscountServiceNotFound()