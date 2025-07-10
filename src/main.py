from fastapi import FastAPI
from api import router
from fastapi.middleware.cors import CORSMiddleware
from endpoints.productos.scripts import router as productos_router

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
