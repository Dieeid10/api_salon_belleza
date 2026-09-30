from datetime import datetime, timedelta
from app.modules.turnos.domain.value_objects import FranjaHoraria

PASO_DEFAULT = timedelta(minutes=15)

def esta_disponible(
    candidata: FranjaHoraria,
    jornada: list[FranjaHoraria],
    ocupadas: list[FranjaHoraria],
) -> bool:
    """La franja entra completa en la jornada y no pisa ningún turno activo."""
    dentro_de_jornada = any(f.contiene(candidata) for f in jornada)
    return dentro_de_jornada and not any(candidata.solapa(o) for o in ocupadas)

def calcular_slots(
    jornada: list[FranjaHoraria],
    ocupadas: list[FranjaHoraria],
    duracion: timedelta,
    ahora: datetime,
    paso: timedelta = PASO_DEFAULT,
) -> list[datetime]:
    """Horarios de inicio posibles para un turno de `duracion`."""
    slots: list[datetime] = []
    for franja in jornada:
        inicio = franja.inicio
        while inicio + duracion <= franja.fin:
            candidata = FranjaHoraria(inicio, inicio + duracion)
            if inicio > ahora and not any(candidata.solapa(o) for o in ocupadas):
                slots.append(inicio)
            inicio += paso
    return slots