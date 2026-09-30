from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from app.modules.clientes.domain.errors import ClienteNoEncontrada
from app.modules.descuentos.domain.entities import TipoDescuento
from app.modules.ventas.application.dto import (
    DetalleVentaResult,
    RegistrarVentaCommand,
    VentaResult,
)
from app.modules.ventas.application.ports import (
    ClienteLookup,
    DescuentoChismeLookup,
    TurnoVentaLookup,
    VentaRepository,
)
from app.modules.ventas.domain.entities import DetalleVenta, Venta
from app.modules.ventas.domain.errors import (
    DescuentoChismeNoDisponible,
    TurnoNoRealizado,
    TurnoVentaNoEncontrado,
    VentaDeTurnoDuplicada,
    VentaNoEncontrada,
)

Reloj = Callable[[], datetime]


def _to_result(venta: Venta) -> VentaResult:
    assert venta.id is not None
    return VentaResult(
        id=venta.id,
        fecha_hora=venta.fecha_hora,
        cliente_id=venta.cliente_id,
        empleado_id=venta.empleado_id,
        turno_id=venta.turno_id,
        descuento_chisme_id=venta.descuento_chisme_id,
        chisme_pct=venta.chisme_pct,
        chisme_detalle=venta.chisme_detalle,
        subtotal=venta.subtotal,
        descuento_chisme=venta.descuento_chisme,
        total=venta.total,
        detalles=[
            DetalleVentaResult(
                servicio_id=detalle.servicio_id,
                descuento_id=detalle.descuento_id,
                precio_lista=detalle.precio_lista,
                descuento_pct=detalle.descuento_pct,
                precio_cobrado=detalle.precio_cobrado,
            )
            for detalle in venta.detalles
        ],
    )


class VentasUseCases:
    def __init__(
        self,
        repo: VentaRepository,
        turnos: TurnoVentaLookup,
        clientes: ClienteLookup,
        descuentos: DescuentoChismeLookup,
        reloj: Reloj,
    ) -> None:
        self._repo = repo
        self._turnos = turnos
        self._clientes = clientes
        self._descuentos = descuentos
        self._reloj = reloj

    def registrar(self, cmd: RegistrarVentaCommand) -> VentaResult:
        turno = self._turnos.obtener_para_venta(cmd.turno_id, bloquear=True)
        if turno is None:
            raise TurnoVentaNoEncontrado()
        if turno.estado != "Realizado":
            raise TurnoNoRealizado()
        if not turno.detalles:
            raise TurnoNoRealizado("El turno realizado no tiene detalles cobrables")
        if self._repo.obtener_por_turno(turno.id) is not None:
            raise VentaDeTurnoDuplicada()
        if self._clientes.obtener(turno.cliente_id) is None:
            raise ClienteNoEncontrada()

        texto_chisme = cmd.chisme_detalle.strip() if cmd.chisme_detalle else None
        descuento_chisme = None
        porcentaje_chisme = Decimal("0")
        if texto_chisme:
            descuento_chisme = self._descuentos.obtener_chisme()
            if (
                descuento_chisme is None
                or not descuento_chisme.activo
                or descuento_chisme.tipo is not TipoDescuento.CHISME
            ):
                raise DescuentoChismeNoDisponible()
            porcentaje_chisme = descuento_chisme.porcentaje

        detalles = [
            DetalleVenta(
                servicio_id=detalle.servicio_id,
                descuento_id=detalle.descuento_id,
                precio_lista=detalle.precio_lista,
                descuento_pct=detalle.descuento_pct,
                precio_cobrado=detalle.precio_reservado,
            )
            for detalle in turno.detalles
        ]
        venta = Venta(
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
        return _to_result(self._repo.crear(venta))

    def obtener(self, venta_id: int) -> VentaResult:
        venta = self._repo.obtener(venta_id)
        if venta is None:
            raise VentaNoEncontrada()
        return _to_result(venta)

    def listar(self) -> list[VentaResult]:
        return [_to_result(venta) for venta in self._repo.listar()]