from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

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
    SaleClientNotFound,
    SaleNotFound,
)

Clock = Callable[[], datetime]


def _to_result(sale: Sale) -> SaleResult:
    """Convierte la entidad de negocio al resultado de aplicación."""
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
    """Coordina las reglas para registrar, consultar y listar ventas."""

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
        """Registra el cobro de un turno realizado y devuelve su resumen."""
        turno = self._turnos.get_for_sale(cmd.turno_id, lock=True)
        if turno is None:
            raise AppointmentForSaleNotFound()
        if not turno.is_completed:
            raise AppointmentNotCompleted()
        if not turno.detalles:
            raise AppointmentNotCompleted("El turno realizado no tiene detalles cobrables")
        if self._repo.get_by_appointment(turno.id) is not None:
            raise DuplicateAppointmentSale()
        if not self._clients.exists(turno.cliente_id):
            raise SaleClientNotFound()

        # El descuento especial solo se consulta cuando la solicitud trae un detalle.
        texto_chisme = cmd.chisme_detalle.strip() if cmd.chisme_detalle else None
        descuento_chisme = None
        porcentaje_chisme = Decimal("0")
        if texto_chisme:
            descuento_chisme = self._descuentos.get_active_gossip_discount()
            if descuento_chisme is None:
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
            fecha_hora = self._reloj(),
            cliente_id = turno.cliente_id,
            empleado_id = cmd.empleado_id,
            turno_id = turno.id,
            descuento_chisme_id = (
                descuento_chisme.id if descuento_chisme is not None else None
            ),
            chisme_pct = porcentaje_chisme,
            chisme_detalle = texto_chisme,
            detalles = detalles,
        )
        return _to_result(self._repo.create(venta))

    def get(self, venta_id: int) -> SaleResult:
        """Busca una venta por id o informa que no existe."""
        venta = self._repo.get(venta_id)
        if venta is None:
            raise SaleNotFound()
        return _to_result(venta)

    def list_all(self) -> list[SaleResult]:
        """Devuelve todas las ventas convertidas a resultados de aplicación."""
        return [_to_result(venta) for venta in self._repo.list_all()]