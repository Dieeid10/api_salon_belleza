"""Adaptadores entre los contratos de turnos y los módulos dueños de los datos."""

from datetime import date, datetime, tzinfo

from app.modules.clientes.infrastructure.persistence.cliente_repository import (
    PsycopgClienteRepository,
)
from app.modules.profesionales.infrastructure.persistence.horario_atencion_repository import (
    PsycopgHorarioAtencionRepository,
)
from app.modules.profesionales.infrastructure.persistence.profesional_repository import (
    PsycopgProfesionalRepository,
)
from app.modules.servicios.infrastructure.persistence.servicio_repository import (
    PsycopgServicioRepository,
)
from app.modules.turnos.application.dto import ServicioInfo
from app.modules.turnos.domain.value_objects import FranjaHoraria


class PsycopgServicioCatalogo:
    def __init__(self, repository: PsycopgServicioRepository) -> None:
        self._repository = repository

    def obtener_activos(self, servicio_ids: list[int]) -> list[ServicioInfo]:
        return [
            ServicioInfo(
                servicio.id,
                servicio.nombre,
                servicio.duracion_min,
                servicio.precio,
            )
            for servicio in self._repository.obtener_activos(servicio_ids)
        ]


class PsycopgClienteRegistro:
    def __init__(self, repository: PsycopgClienteRepository) -> None:
        self._repository = repository

    def obtener_o_crear(self, nombre: str, apellido: str, telefono: str) -> int:
        return self._repository.obtener_o_crear_para_reserva(
            nombre,
            apellido,
            telefono,
        )


class PsycopgAgendaProfesional:
    def __init__(
        self,
        profesionales: PsycopgProfesionalRepository,
        horarios: PsycopgHorarioAtencionRepository,
        zona: tzinfo,
    ) -> None:
        self._profesionales = profesionales
        self._horarios = horarios
        self._zona = zona

    def esta_activo(self, profesional_id: int) -> bool:
        return self._profesionales.esta_activo(profesional_id)

    def jornada(self, profesional_id: int, fecha: date) -> list[FranjaHoraria]:
        return [
            FranjaHoraria(
                datetime.combine(fecha, horario.hora_apertura, tzinfo=self._zona),
                datetime.combine(fecha, horario.hora_cierre, tzinfo=self._zona),
            )
            for horario in self._horarios.jornada(profesional_id, fecha)
        ]