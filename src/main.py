from fastapi import FastAPI
from api import router
from fastapi.middleware.cors import CORSMiddleware
#from endpoints.scripts.producto import router as productos_router
from endpoints.scripts.polizas_canceladas import router as canceladas_router
from endpoints.scripts.proximas_vigencias import router as vigencias_router
from endpoints.scripts.historial_productos import router as historial_router
from endpoints.preguntas.preguntar import router as preguntar_router
from endpoints.finalizar.finalizar import router as finalizar_router
import os

SHOW_DOCS = os.getenv("SHOW_DOCS", "true").lower() == "true"

#app = FastAPI()

app = FastAPI(
    docs_url="/docs" if SHOW_DOCS else None,
    redoc_url="/redoc" if SHOW_DOCS else None,
    openapi_url="/openapi.json" if SHOW_DOCS else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
#app.include_router(productos_router)
app.include_router(historial_router)
app.include_router(canceladas_router)
app.include_router(vigencias_router)
app.include_router(preguntar_router)
app.include_router(finalizar_router)
