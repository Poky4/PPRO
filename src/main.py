import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.core.config import settings
from src.api.v1.api_router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Informační systém pro soukromou lékařskou praxi (Varianta A – Rezervace v ordinaci).\n\n"
        "Semestrální projekt pro předmět **Pokročilé programování (PPRO)**, FIM UHK."
    ),
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware pro klientské rozhraní
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statické soubory (CSS, JS, obrázky)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_spa():
    """Zobrazení webového uživatelského rozhraní."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Monitoring"], summary="Healthcheck stavu aplikace")
def health_check():
    """Kontrola běžící aplikace pro Docker a monitorovací nástroje."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


# Připojení hlavního API směrovače
app.include_router(api_router, prefix=settings.API_V1_STR)
