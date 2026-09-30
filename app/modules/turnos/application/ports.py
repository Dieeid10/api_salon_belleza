from collections.abc import Callable
from datetime import date, datetime
from typing import Protocol

from app.modules.turnos.application.dto import ServicioInfo, TurnoVentaInfo
from app.modules.turnos.domain.entities import Turno
from app.modules.turnos.domain.value_objects import EstadoTurno, FranjaHoraria

Reloj = Callable[[], datetime]  # debe devolver un datetime con zona horaria


class TurnoRepository(Protocol):
    def crear(self, turno: Turno) -> Turno: pass
    def obtener(self, turno_id: int, bloquear: bool = False) -> Turno | None: pass
    def actualizar_estado(self, turno: Turno) -> None: pass
    def listar_ocupados(
        self, profesional_id: int, desde: datetime, hasta: datetime
    ) -> list[FranjaHoraria]: pass
    def listar(
        self,
        desde: datetime,
        hasta: datetime,
        profesional_id: int | None = None,
        estado: EstadoTurno | None = None,
    ) -> list[Turno]: pass
    def obtener_para_venta(self, turno_id: int, bloquear: bool = False) -> TurnoVentaInfo | None: pass


class ServicioCatalogo(Protocol):
    def obtener_activos(self, servicio_ids: list[int]) -> list[ServicioInfo]: pass


class ClienteRegistro(Protocol):
    def obtener_o_crear(self, nombre: str, apellido: str, telefono: str) -> int: pass


class AgendaProfesional(Protocol):
    def esta_activo(self, profesional_id: int) -> bool: pass
    def jornada(self, profesional_id: int, fecha: date) -> list[FranjaHoraria]: pass


class TurnosUnitOfWork(Protocol):
    turnos: TurnoRepository
    servicios: ServicioCatalogo
    clientes: ClienteRegistro
    agenda: AgendaProfesional

    def __enter__(self) -> "TurnosUnitOfWork": pass
    def __exit__(self, exc_type, exc, tb) -> bool | None: pass