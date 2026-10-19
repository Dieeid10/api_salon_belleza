from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateClientCommand:
    first_name: str
    last_name: str
    phone: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class UpdateClientCommand:
    client_id: int
    first_name: str
    last_name: str
    phone: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class ClientResult:
    id: int
    first_name: str
    last_name: str
    phone: str | None
    email: str | None
    is_active: bool
    created_at: datetime