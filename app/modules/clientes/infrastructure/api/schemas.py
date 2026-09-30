from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class ClienteRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    telefono: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validar_contacto(self):
        if self.telefono is None and self.email is None:
            raise ValueError("La clienta debe tener teléfono o email de contacto")
        return self


class ClienteResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: str | None
    email: str | None
    activo: bool
    fecha_creacion: datetime