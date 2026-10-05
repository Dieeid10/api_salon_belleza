from app.modules.turnos.application.dto import DetalleResult, TurnoResult
from app.modules.turnos.domain.entities import Turno

def to_result(t: Turno) -> TurnoResult:
    return TurnoResult(
        id=t.id,
        cliente_id=t.cliente_id,
        profesional_id=t.profesional_id,
        inicio=t.franja.inicio,
        fin=t.franja.fin,
        estado=t.estado.value,
        total=t.total,
        detalles=[
            DetalleResult(d.servicio_id, d.nombre, d.duracion_min, d.precio)
            for d in t.detalles
        ],
    )