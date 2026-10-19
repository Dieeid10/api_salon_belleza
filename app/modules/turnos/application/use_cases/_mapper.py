from app.modules.turnos.application.dto import AppointmentDetailResult, AppointmentResult
from app.modules.turnos.domain.entities import Turno

def to_result(t: Turno) -> AppointmentResult:
    return AppointmentResult(
        id=t.id,
        cliente_id=t.cliente_id,
        profesional_id=t.profesional_id,
        inicio=t.franja.inicio,
        fin=t.franja.fin,
        estado=t.estado.value,
        total=t.total,
        detalles=[
            AppointmentDetailResult(d.servicio_id, d.nombre, d.duracion_min, d.precio)
            for d in t.detalles
        ],
    )