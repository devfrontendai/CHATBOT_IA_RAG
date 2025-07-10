from fastapi import FastAPI
from api import router
from fastapi.middleware.cors import CORSMiddleware
from endpoints.scripts.producto import router as productos_router
from endpoints.scripts.polizas_canceladas import router as canceladas_router
from endpoints.scripts.proximas_vigencias import router as vigencias_router
from endpoints.scripts.historial_productos import router as historial_router
from endpoints.scripts.vigencias import router as vigencias_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:3000"] para tu front local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(productos_router)
app.include_router(canceladas_router)
app.include_router(vigencias_router)
app.include_router(historial_router)
app.include_router(vigencias_router)
