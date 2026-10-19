from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ClientRequest(BaseModel):
    first_name: str = Field(alias="nombre", min_length=1, max_length=100)
    last_name: str = Field(alias="apellido", min_length=1, max_length=100)
    phone: str | None = Field(default=None, alias="telefono", max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_contact_info(self):
        if self.phone is None and self.email is None:
            raise ValueError("La clienta debe tener teléfono o email de contacto")
        return self


class ClientResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    first_name: str = Field(alias="nombre")
    last_name: str = Field(alias="apellido")
    phone: str | None = Field(alias="telefono")
    email: str | None
    is_active: bool = Field(alias="activo")
    created_at: datetime = Field(alias="fecha_creacion")