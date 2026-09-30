from app.modules.profesionales.application.dto import (
    ActualizarProfesionalCommand,
    CrearProfesionalCommand,
    ProfesionalResult,
)
from app.modules.profesionales.application.ports import ProfesionalRepository
from app.modules.profesionales.domain.entities import Profesional
from app.modules.profesionales.domain.errors import ProfesionalNoEncontrado

# Mapper
def _to_result(p: Profesional) -> ProfesionalResult:
    return ProfesionalResult(
        id=p.id, nombre=p.nombre, perfil_id=p.perfil_id, activo=p.activo
    )


class ProfesionalesUseCases:
    def __init__(self, repo: ProfesionalRepository) -> None:
        self._repo = repo

    def crear(self, cmd: CrearProfesionalCommand) -> ProfesionalResult:
        profesional = Profesional(nombre=cmd.nombre, perfil_id=cmd.perfil_id)
        return _to_result(self._repo.crear(profesional))

    def obtener(self, profesional_id: int) -> ProfesionalResult:
        return _to_result(self._get_or_fail(profesional_id))

    def listar(self, solo_activos: bool = True) -> list[ProfesionalResult]:
        return [_to_result(p) for p in self._repo.listar(solo_activos)]

    def actualizar(self, cmd: ActualizarProfesionalCommand) -> ProfesionalResult:
        profesional = self._get_or_fail(cmd.profesional_id)
        profesional.actualizar_datos(cmd.nombre, cmd.perfil_id)
        return _to_result(self._repo.actualizar(profesional))

    def desactivar(self, profesional_id: int) -> None:
        profesional = self._get_or_fail(profesional_id)
        profesional.desactivar()
        self._repo.actualizar(profesional)

    def _get_or_fail(self, profesional_id: int) -> Profesional:
        profesional = self._repo.obtener(profesional_id)
        if profesional is None:
            raise ProfesionalNoEncontrado()
        return profesional