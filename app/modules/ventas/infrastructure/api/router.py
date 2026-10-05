from dataclasses import asdict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.ventas.application.dto import RegistrarVentaCommand
from app.modules.ventas.application.use_cases import VentasUseCases
from app.modules.ventas.infrastructure.api.dependencies import get_use_cases
from app.modules.ventas.infrastructure.api.schemas import (
    RegistrarVentaRequest,
    VentaResponse,
)
from app.shared.security import require_role

router = APIRouter()
personal_del_salon = require_role("dueno", "vendedor")


@router.get("/", response_model=list[VentaResponse])
def listar(
    _: dict = Depends(personal_del_salon),
    uc: VentasUseCases = Depends(get_use_cases),
):
    return [asdict(venta) for venta in uc.listar()]


@router.get("/{venta_id}", response_model=VentaResponse)
def obtener(
    venta_id: int,
    _: dict = Depends(personal_del_salon),
    uc: VentasUseCases = Depends(get_use_cases),
):
    return asdict(uc.obtener(venta_id))


@router.post("/", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
def registrar(
    body: RegistrarVentaRequest,
    user: dict = Depends(personal_del_salon),
    uc: VentasUseCases = Depends(get_use_cases),
):
    try:
        empleado_id = UUID(user["sub"])
    except (KeyError, ValueError) as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario inválido") from error
    command = RegistrarVentaCommand(
        turno_id=body.turno_id,
        empleado_id=empleado_id,
        chisme_detalle=body.chisme_detalle,
    )
    return asdict(uc.registrar(command))