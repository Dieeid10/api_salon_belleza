from dataclasses import dataclass
from datetime import datetime

from app.shared.error import ValidationError


@dataclass
class Client:
    first_name: str
    last_name: str
    phone: str | None = None
    email: str | None = None
    is_active: bool = True
    id: int | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        self.phone = self.phone.strip() if self.phone else None
        self.email = self.email.strip().lower() if self.email else None

        if not self.first_name:
            raise ValidationError("El nombre de la clienta es obligatorio")
        if len(self.first_name) > 100:
            raise ValidationError("El nombre no puede superar 100 caracteres")
        if not self.last_name:
            raise ValidationError("El apellido de la clienta es obligatorio")
        if len(self.last_name) > 100:
            raise ValidationError("El apellido no puede superar 100 caracteres")
        if self.phone is not None and len(self.phone) > 50:
            raise ValidationError("El teléfono no puede superar 50 caracteres")
        if self.email is not None and len(self.email) > 100:
            raise ValidationError("El email no puede superar 100 caracteres")
        if self.phone is None and self.email is None:
            raise ValidationError("La clienta debe tener teléfono o email de contacto")

    def update_details(
        self,
        first_name: str,
        last_name: str,
        phone: str | None,
        email: str | None,
    ) -> None:
        updated = Client(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            is_active=self.is_active,
            id=self.id,
            created_at=self.created_at,
        )
        self.first_name = updated.first_name
        self.last_name = updated.last_name
        self.phone = updated.phone
        self.email = updated.email

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True