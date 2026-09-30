from dataclasses import asdict

from fastapi import APIRouter, Depends

from app.modules.auth.application.use_cases import AuthUseCases
from app.modules.auth.infrastructure.api.schemas import (
    LoginRequest, RefreshRequest, SesionResponse,
)
from app.modules.auth.infrastructure.supabase_auth_provider import SupabaseAuthProvider

router = APIRouter()

def get_use_cases() -> AuthUseCases:
    return AuthUseCases(SupabaseAuthProvider())


@router.post("/login", response_model=SesionResponse)
def login(body: LoginRequest, uc: AuthUseCases = Depends(get_use_cases)):
    return SesionResponse(**asdict(uc.login(body.email, body.password)))


@router.post("/refresh", response_model=SesionResponse)
def refresh(body: RefreshRequest, uc: AuthUseCases = Depends(get_use_cases)):
    return SesionResponse(**asdict(uc.refrescar(body.refresh_token)))