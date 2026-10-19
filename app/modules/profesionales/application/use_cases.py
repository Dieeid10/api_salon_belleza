from app.modules.profesionales.application.dto import (
    CreateProfessionalCommand,
    ProfessionalResult,
    UpdateProfessionalCommand,
)
from app.modules.profesionales.application.ports import ProfessionalRepository
from app.modules.profesionales.domain.entities import Professional
from app.modules.profesionales.domain.errors import ProfessionalNotFound

# Mapper
def _to_result(p: Professional) -> ProfessionalResult:
    return ProfessionalResult(
        id=p.id, nombre=p.nombre, perfil_id=p.perfil_id, activo=p.activo
    )


class ProfessionalUseCases:
    def __init__(self, repo: ProfessionalRepository) -> None:
        self._repo = repo

    def create(self, cmd: CreateProfessionalCommand) -> ProfessionalResult:
        profesional = Professional(nombre=cmd.nombre, perfil_id=cmd.perfil_id)
        return _to_result(self._repo.create(profesional))

    def get(self, profesional_id: int) -> ProfessionalResult:
        return _to_result(self._get_or_raise(profesional_id))

    def list_all(self, solo_activos: bool = True) -> list[ProfessionalResult]:
        return [_to_result(p) for p in self._repo.list_all(solo_activos)]

    def update(self, cmd: UpdateProfessionalCommand) -> ProfessionalResult:
        profesional = self._get_or_raise(cmd.profesional_id)
        profesional.update_details(cmd.nombre, cmd.perfil_id)
        return _to_result(self._repo.update(profesional))

    def deactivate(self, profesional_id: int) -> None:
        profesional = self._get_or_raise(profesional_id)
        profesional.deactivate()
        self._repo.update(profesional)

    def _get_or_raise(self, profesional_id: int) -> Professional:
        profesional = self._repo.get(profesional_id)
        if profesional is None:
            raise ProfessionalNotFound()
        return profesional