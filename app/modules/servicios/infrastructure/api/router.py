from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.modules.servicios.application.dto import (
    ActualizarServicioCommand,
    CrearServicioCommand,
)
from app.modules.servicios.application.use_cases import ServiciosUseCases
from app.modules.servicios.infrastructure.api.dependencies import get_use_cases
from app.modules.servicios.infrastructure.api.schemas import (
    ServicioRequest,
    ServicioResponse,
)
from app.shared.security import require_role

router = APIRouter()
admin = [Depends(require_role("dueno", "vendedor"))]


@router.get("/", response_model=list[ServicioResponse])
def listar_publicos(uc: ServiciosUseCases = Depends(get_use_cases)):
    return [asdict(servicio) for servicio in uc.listar()]


@router.get("/gestion", response_model=list[ServicioResponse], dependencies=admin)
def listar_gestion(uc: ServiciosUseCases = Depends(get_use_cases)):
    return [
        asdict(servicio)
        for servicio in uc.listar(solo_activos=False, solo_visibles_online=False)
    ]


@router.get("/gestion/{servicio_id}", response_model=ServicioResponse, dependencies=admin)
def obtener_gestion(servicio_id: int, uc: ServiciosUseCases = Depends(get_use_cases)):
    return asdict(uc.obtener(servicio_id))


@router.get("/{servicio_id}", response_model=ServicioResponse)
def obtener_publico(servicio_id: int, uc: ServiciosUseCases = Depends(get_use_cases)):
    return asdict(uc.obtener_publico(servicio_id))


@router.post(
    "/",
    response_model=ServicioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=admin,
)
def crear(body: ServicioRequest, uc: ServiciosUseCases = Depends(get_use_cases)):
    return asdict(uc.crear(CrearServicioCommand(**body.model_dump())))


@router.put("/{servicio_id}", response_model=ServicioResponse, dependencies=admin)
def actualizar(
    servicio_id: int,
    body: ServicioRequest,
    uc: ServiciosUseCases = Depends(get_use_cases),
):
    command = ActualizarServicioCommand(
        servicio_id=servicio_id,
        **body.model_dump(),
    )
    return asdict(uc.actualizar(command))


@router.delete(
    "/{servicio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=admin,
)
def desactivar(servicio_id: int, uc: ServiciosUseCases = Depends(get_use_cases)):
    uc.desactivar(servicio_id)