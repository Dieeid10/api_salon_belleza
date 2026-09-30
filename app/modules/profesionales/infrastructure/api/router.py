from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.modules.profesionales.application.dto import (
    ActualizarProfesionalCommand,
    CrearProfesionalCommand,
)
from app.modules.profesionales.application.use_cases import ProfesionalesUseCases
from app.modules.profesionales.infrastructure.api.dependencies import get_use_cases
from app.modules.profesionales.infrastructure.api.schemas import (
    ProfesionalRequest,
    ProfesionalResponse,
)
from app.shared.security import require_role

router = APIRouter()
admin = [Depends(require_role("dueno"))]


@router.get("/", response_model=list[ProfesionalResponse])
def listar(solo_activos: bool = True, uc: ProfesionalesUseCases = Depends(get_use_cases)):
    return [ProfesionalResponse(**asdict(r)) for r in uc.listar(solo_activos)]


@router.get("/{profesional_id}", response_model=ProfesionalResponse)
def obtener(profesional_id: int, uc: ProfesionalesUseCases = Depends(get_use_cases)):
    return ProfesionalResponse(**asdict(uc.obtener(profesional_id)))


@router.post("/", response_model=ProfesionalResponse,
             status_code=status.HTTP_201_CREATED, dependencies=admin)
def crear(body: ProfesionalRequest, uc: ProfesionalesUseCases = Depends(get_use_cases)):
    result = uc.crear(CrearProfesionalCommand(**body.model_dump()))
    return ProfesionalResponse(**asdict(result))


@router.put("/{profesional_id}", response_model=ProfesionalResponse, dependencies=admin)
def actualizar(profesional_id: int, body: ProfesionalRequest,
               uc: ProfesionalesUseCases = Depends(get_use_cases)):
    cmd = ActualizarProfesionalCommand(profesional_id=profesional_id, **body.model_dump())
    return ProfesionalResponse(**asdict(uc.actualizar(cmd)))


@router.delete("/{profesional_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin)
def desactivar(profesional_id: int, uc: ProfesionalesUseCases = Depends(get_use_cases)):
    uc.desactivar(profesional_id)