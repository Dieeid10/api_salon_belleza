from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, status

from app.modules.descuentos.application.dto import (
    CreateDiscountCommand,
    UpdateDiscountCommand,
)
from app.modules.descuentos.application.use_cases import DiscountUseCases
from app.modules.descuentos.infrastructure.api.dependencies import get_use_cases
from app.modules.descuentos.infrastructure.api.schemas import (
    DescuentoRequest,
    DescuentoResponse,
)
from app.shared.security import require_role

router = APIRouter()
duena = [Depends(require_role("dueno"))]
_ZONA_HORARIA = ZoneInfo("America/Argentina/Buenos_Aires")


@router.get("/", response_model=list[DescuentoResponse])
def listar_publicos(uc: DiscountUseCases = Depends(get_use_cases)):
    hoy = datetime.now(_ZONA_HORARIA).date()
    return [asdict(descuento) for descuento in uc.list_public(hoy)]


@router.get("/gestion", response_model=list[DescuentoResponse], dependencies=duena)
def listar_gestion(uc: DiscountUseCases = Depends(get_use_cases)):
    return [asdict(descuento) for descuento in uc.list_all()]


@router.get(
    "/gestion/{descuento_id}",
    response_model=DescuentoResponse,
    dependencies=duena,
)
def obtener_gestion(
    descuento_id: int,
    uc: DiscountUseCases = Depends(get_use_cases),
):
    return asdict(uc.get(descuento_id))


@router.post(
    "/",
    response_model=DescuentoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=duena,
)
def crear(body: DescuentoRequest, uc: DiscountUseCases = Depends(get_use_cases)):
    return asdict(uc.create(CreateDiscountCommand(**body.model_dump())))


@router.put(
    "/{descuento_id}",
    response_model=DescuentoResponse,
    dependencies=duena,
)
def actualizar(
    descuento_id: int,
    body: DescuentoRequest,
    uc: DiscountUseCases = Depends(get_use_cases),
):
    command = UpdateDiscountCommand(
        descuento_id=descuento_id,
        **body.model_dump(),
    )
    return asdict(uc.update(command))


@router.delete(
    "/{descuento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=duena,
)
def desactivar(
    descuento_id: int,
    uc: DiscountUseCases = Depends(get_use_cases),
):
    uc.deactivate(descuento_id)