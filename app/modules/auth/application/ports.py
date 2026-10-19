from typing import Protocol

from app.modules.auth.application.dto import SessionResult


class AuthProvider(Protocol):
    def login(self, email: str, password: str) -> SessionResult: ...
    def refresh(self, refresh_token: str) -> SessionResult: ...