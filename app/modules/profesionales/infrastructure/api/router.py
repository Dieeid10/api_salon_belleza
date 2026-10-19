from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.modules.profesionales.application.dto import (
    CreateProfessionalCommand,
    UpdateProfessionalCommand,
)
from app.modules.profesionales.application.use_cases import ProfessionalUseCases
from app.modules.profesionales.infrastructure.api.dependencies import get_use_cases
from app.modules.profesionales.infrastructure.api.schemas import (
    ProfesionalRequest,
    ProfesionalResponse,
)
from app.shared.security import require_role

router = APIRouter()
admin = [Depends(require_role("dueno"))]


@router.get("/", response_model=list[ProfesionalResponse])
def listar(solo_activos: bool = True, uc: ProfessionalUseCases = Depends(get_use_cases)):
    return [ProfesionalResponse(**asdict(r)) for r in uc.list_all(solo_activos)]


@router.get("/{profesional_id}", response_model=ProfesionalResponse)
def obtener(profesional_id: int, uc: ProfessionalUseCases = Depends(get_use_cases)):
    return ProfesionalResponse(**asdict(uc.get(profesional_id)))


@router.post("/", response_model=ProfesionalResponse,
             status_code=status.HTTP_201_CREATED, dependencies=admin)
def crear(body: ProfesionalRequest, uc: ProfessionalUseCases = Depends(get_use_cases)):
    result = uc.create(CreateProfessionalCommand(**body.model_dump()))
    return ProfesionalResponse(**asdict(result))


@router.put("/{profesional_id}", response_model=ProfesionalResponse, dependencies=admin)
def actualizar(profesional_id: int, body: ProfesionalRequest,
               uc: ProfessionalUseCases = Depends(get_use_cases)):
    cmd = UpdateProfessionalCommand(profesional_id=profesional_id, **body.model_dump())
    return ProfesionalResponse(**asdict(uc.update(cmd)))


@router.delete("/{profesional_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin)
def desactivar(profesional_id: int, uc: ProfessionalUseCases = Depends(get_use_cases)):
    uc.deactivate(profesional_id)