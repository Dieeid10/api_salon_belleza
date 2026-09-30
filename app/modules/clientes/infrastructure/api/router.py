from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.modules.clientes.application.dto import (
    ActualizarClienteCommand,
    CrearClienteCommand,
)
from app.modules.clientes.application.use_cases import ClientesUseCases
from app.modules.clientes.infrastructure.api.dependencies import get_use_cases
from app.modules.clientes.infrastructure.api.schemas import (
    ClienteRequest,
    ClienteResponse,
)
from app.shared.security import require_role

router = APIRouter(dependencies=[Depends(require_role("dueno", "vendedor"))])


@router.get("/", response_model=list[ClienteResponse])
def listar(solo_activos: bool = True, uc: ClientesUseCases = Depends(get_use_cases)):
    return [asdict(cliente) for cliente in uc.listar(solo_activos)]


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener(cliente_id: int, uc: ClientesUseCases = Depends(get_use_cases)):
    return asdict(uc.obtener(cliente_id))


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear(body: ClienteRequest, uc: ClientesUseCases = Depends(get_use_cases)):
    return asdict(uc.crear(CrearClienteCommand(**body.model_dump())))


@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar(
    cliente_id: int,
    body: ClienteRequest,
    uc: ClientesUseCases = Depends(get_use_cases),
):
    command = ActualizarClienteCommand(cliente_id=cliente_id, **body.model_dump())
    return asdict(uc.actualizar(command))


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar(cliente_id: int, uc: ClientesUseCases = Depends(get_use_cases)):
    uc.desactivar(cliente_id)