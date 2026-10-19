from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.modules.clientes.application.dto import (
    CreateClientCommand,
    UpdateClientCommand,
)
from app.modules.clientes.application.use_cases import ClientUseCases
from app.modules.clientes.infrastructure.api.dependencies import get_use_cases
from app.modules.clientes.infrastructure.api.schemas import (
    ClientRequest,
    ClientResponse,
)
from app.shared.security import require_role

router = APIRouter(dependencies=[Depends(require_role("dueno", "vendedor"))])


@router.get("/", response_model=list[ClientResponse])
def listar(solo_activos: bool = True, uc: ClientUseCases = Depends(get_use_cases)):
    return [asdict(client) for client in uc.list_all(solo_activos)]


@router.get("/{cliente_id}", response_model=ClientResponse)
def obtener(cliente_id: int, uc: ClientUseCases = Depends(get_use_cases)):
    return asdict(uc.get(cliente_id))


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def crear(body: ClientRequest, uc: ClientUseCases = Depends(get_use_cases)):
    command = CreateClientCommand(
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        email=body.email,
    )
    return asdict(uc.create(command))

@router.patch("/{cliente_id}/activar", status_code=status.HTTP_204_NO_CONTENT)
def activar(cliente_id: int, uc: ClientUseCases = Depends(get_use_cases)):
    uc.activate(cliente_id)

@router.put("/{cliente_id}", response_model=ClientResponse)
def actualizar(cliente_id: int, body: ClientRequest, uc: ClientUseCases = Depends(get_use_cases)):
    command = UpdateClientCommand(
        client_id=cliente_id,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        email=body.email,
    )
    return asdict(uc.update(command))


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar(cliente_id: int, uc: ClientUseCases = Depends(get_use_cases)):
    uc.deactivate(cliente_id)