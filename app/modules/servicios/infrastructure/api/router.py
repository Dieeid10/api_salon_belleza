from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.modules.servicios.application.dto import (
    CreateServiceCommand,
    UpdateServiceCommand,
)
from app.modules.servicios.application.use_cases import ServiceUseCases
from app.modules.servicios.infrastructure.api.dependencies import get_use_cases
from app.modules.servicios.infrastructure.api.schemas import (
    ServicioRequest,
    ServicioResponse,
)
from app.shared.security import require_role

router = APIRouter()
admin = [Depends(require_role("dueno", "vendedor"))]


@router.get("/", response_model=list[ServicioResponse])
def listar_publicos(uc: ServiceUseCases = Depends(get_use_cases)):
    return [asdict(servicio) for servicio in uc.list_all()]


@router.get("/gestion", response_model=list[ServicioResponse], dependencies=admin)
def listar_gestion(uc: ServiceUseCases = Depends(get_use_cases)):
    return [
        asdict(servicio)
        for servicio in uc.list_all(active_only=False, online_only=False)
    ]


@router.get("/gestion/{servicio_id}", response_model=ServicioResponse, dependencies=admin)
def obtener_gestion(servicio_id: int, uc: ServiceUseCases = Depends(get_use_cases)):
    return asdict(uc.get(servicio_id))


@router.get("/{servicio_id}", response_model=ServicioResponse)
def obtener_publico(servicio_id: int, uc: ServiceUseCases = Depends(get_use_cases)):
    return asdict(uc.get_public(servicio_id))


@router.post(
    "/",
    response_model=ServicioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=admin,
)
def crear(body: ServicioRequest, uc: ServiceUseCases = Depends(get_use_cases)):
    return asdict(uc.create(CreateServiceCommand(**body.model_dump())))


@router.put("/{servicio_id}", response_model=ServicioResponse, dependencies=admin)
def actualizar(
    servicio_id: int,
    body: ServicioRequest,
    uc: ServiceUseCases = Depends(get_use_cases),
):
    command = UpdateServiceCommand(
        servicio_id=servicio_id,
        **body.model_dump(),
    )
    return asdict(uc.update(command))


@router.delete(
    "/{servicio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=admin,
)
def desactivar(servicio_id: int, uc: ServiceUseCases = Depends(get_use_cases)):
    uc.deactivate(servicio_id)