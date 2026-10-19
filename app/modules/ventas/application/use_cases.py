from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from app.modules.clientes.domain.errors import ClientNotFound
from app.modules.descuentos.domain.entities import TipoDescuento
from app.modules.ventas.application.dto import (
    RegisterSaleCommand,
    SaleDetailResult,
    SaleResult,
)
from app.modules.ventas.application.ports import (
    AppointmentSaleLookup,
    ClientLookup,
    GossipDiscountLookup,
    SaleRepository,
)
from app.modules.ventas.domain.entities import Sale, SaleDetail
from app.modules.ventas.domain.errors import (
    AppointmentForSaleNotFound,
    AppointmentNotCompleted,
    DuplicateAppointmentSale,
    GossipDiscountUnavailable,
    SaleNotFound,
)

Clock = Callable[[], datetime]


def _to_result(sale: Sale) -> SaleResult:
    assert sale.id is not None
    return SaleResult(
        id = sale.id,
        fecha_hora = sale.fecha_hora,
        cliente_id = sale.cliente_id,
        empleado_id = sale.empleado_id,
        turno_id = sale.turno_id,
        descuento_chisme_id = sale.descuento_chisme_id,
        chisme_pct = sale.chisme_pct,
        chisme_detalle = sale.chisme_detalle,
        subtotal = sale.subtotal,
        descuento_chisme = sale.descuento_chisme,
        total = sale.total,
        detalles = [
                SaleDetailResult(
                servicio_id=detalle.servicio_id,
                descuento_id=detalle.descuento_id,
                precio_lista=detalle.precio_lista,
                descuento_pct=detalle.descuento_pct,
                precio_cobrado=detalle.precio_cobrado,
            )
            for detalle in sale.detalles
        ]
    )


class SaleUseCases:
    def __init__(
        self,
        repo: SaleRepository,
        turnos: AppointmentSaleLookup,
        clients: ClientLookup,
        descuentos: GossipDiscountLookup,
        reloj: Clock,
    ) -> None:
        self._repo = repo
        self._turnos = turnos
        self._clients = clients
        self._descuentos = descuentos
        self._reloj = reloj

    def register(self, cmd: RegisterSaleCommand) -> SaleResult:
        turno = self._turnos.get_for_sale(cmd.turno_id, lock=True)
        if turno is None:
            raise AppointmentForSaleNotFound()
        if turno.estado != "Realizado":
            raise AppointmentNotCompleted()
        if not turno.detalles:
            raise AppointmentNotCompleted("El turno realizado no tiene detalles cobrables")
        if self._repo.get_by_appointment(turno.id) is not None:
            raise DuplicateAppointmentSale()
        if self._clients.get(turno.cliente_id) is None:
            raise ClientNotFound()

        texto_chisme = cmd.chisme_detalle.strip() if cmd.chisme_detalle else None
        descuento_chisme = None
        porcentaje_chisme = Decimal("0")
        if texto_chisme:
            descuento_chisme = self._descuentos.get_gossip_discount()
            if (
                descuento_chisme is None
                or not descuento_chisme.activo
                or descuento_chisme.tipo is not TipoDescuento.CHISME
            ):
                raise GossipDiscountUnavailable()
            porcentaje_chisme = descuento_chisme.porcentaje

        detalles = [
            SaleDetail(
                servicio_id=detalle.servicio_id,
                descuento_id=detalle.descuento_id,
                precio_lista=detalle.precio_lista,
                descuento_pct=detalle.descuento_pct,
                precio_cobrado=detalle.precio_reservado,
            )
            for detalle in turno.detalles
        ]
        venta = Sale(
            fecha_hora=self._reloj(),
            cliente_id=turno.cliente_id,
            empleado_id=cmd.empleado_id,
            turno_id=turno.id,
            descuento_chisme_id=(
                descuento_chisme.id if descuento_chisme is not None else None
            ),
            chisme_pct=porcentaje_chisme,
            chisme_detalle=texto_chisme,
            detalles=detalles,
        )
        return _to_result(self._repo.create(venta))

    def get(self, venta_id: int) -> SaleResult:
        venta = self._repo.get(venta_id)
        if venta is None:
            raise SaleNotFound()
        return _to_result(venta)

    def list_all(self) -> list[SaleResult]:
        return [_to_result(venta) for venta in self._repo.list_all()]