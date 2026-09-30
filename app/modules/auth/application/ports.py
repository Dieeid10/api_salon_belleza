from typing import Protocol

from app.modules.auth.application.dto import SesionResult


class AuthProvider(Protocol):
    def login(self, email: str, password: str) -> SesionResult: pass
    def refrescar(self, refresh_token: str) -> SesionResult: pass