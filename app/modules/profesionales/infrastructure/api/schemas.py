from pydantic import BaseModel, Field


class ProfesionalRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    perfil_id: str | None = None


class ProfesionalResponse(BaseModel):
    id: int
    nombre: str
    perfil_id: str | None
    activo: bool