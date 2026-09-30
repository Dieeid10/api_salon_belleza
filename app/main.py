import logging
from contextlib import asynccontextmanager
    
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.modules.auth.infrastructure.api.router import router as auth_router
from app.modules.servicios.infrastructure.api.router import router as servicios_router
from app.modules.descuentos.infrastructure.api.router import router as descuentos_router
from app.modules.clientes.infrastructure.api.router import router as clientes_router
from app.modules.profesionales.infrastructure.api.router import router as profesionales_router
from app.modules.turnos.infrastructure.api.router_admin import router as turnos_admin_router
from app.modules.turnos.infrastructure.api.router_publico import router as turnos_publico_router
from app.modules.ventas.infrastructure.api.router import router as ventas_router
from app.shared.error import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.shared.config import settings
from app.shared.infrastructure.db.database import db

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arranque: abre el pool una sola vez
    db.open()
    logger.info("Pool de conexiones abierto")
    yield
    # Apagado: cierra el pool y libera las conexiones
    db.close()
    logger.info("Pool de conexiones cerrado")


app = FastAPI(
    title="Salón API",
    version="0.1.0",
    lifespan=lifespan,
    # Opcional: ocultar la documentación en producción
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)


@app.exception_handler(DomainError)
async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, ForbiddenError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(servicios_router, prefix="/servicios", tags=["servicios"])
app.include_router(clientes_router, prefix="/clientes", tags=["clientes"])
app.include_router(descuentos_router, prefix="/descuentos", tags=["descuentos"])
app.include_router(ventas_router, prefix="/ventas", tags=["ventas"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(profesionales_router, prefix="/profesionales", tags=["profesionales"])
app.include_router(turnos_publico_router, prefix="/turnos", tags=["turnos"])
app.include_router(
    turnos_admin_router,
    prefix="/admin/turnos",
    tags=["turnos-admin"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment != "production",
    )
