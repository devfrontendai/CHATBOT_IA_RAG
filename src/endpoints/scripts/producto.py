# endpoints/productos.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

# Modelos de respuesta
class Poliza(BaseModel):
    numero: str
    estatus: str
    producto: str
    plan: str
    motivo_cancelacion: Optional[str] = None

class ProductosResponse(BaseModel):
    nombre: str
    polizas: List[Poliza]

# Endpoint dummy: /productos/{asegurado_id}
@router.get("/productos/{asegurado_id}", response_model=ProductosResponse)
def get_productos(asegurado_id: str):
    # --- AQUÍ LLAMARÁS TU BACKEND DE LARAVEL ---
    # Ejemplo: 
    # import requests
    # response = requests.get(f"http://laravel-back/api/polizas/{asegurado_id}")
    # return response.json()
    
    # Dummy aleatorio para testing frontend:
    nombres = ["Alfredo Tiprotec", "Daniel Camacho", "Juan Pérez", "María García"]
    productos = ["TRAVEL ANNUAL 4.0", "GUARD FAMILY", "AMEX GUARD 3.1", "GNP LIFE"]
    planes = ["FAMILIAR ADVANCED", "INDIVIDUAL ELITE", "FAMILIAR ESSENTIAL"]
    estatuses = ["Vigente", "Cancelada"]
    motivos = [None, "DUPLICIDAD POLIZA", "SOLICITUD CLIENTE", "IMPAGO"]

    polizas = []
    for i in range(random.randint(1, 5)):
        polizas.append(
            Poliza(
                numero=str(random.randint(9000000, 9999999)),
                estatus=random.choice(estatuses),
                producto=random.choice(productos),
                plan=random.choice(planes),
                motivo_cancelacion=random.choice(motivos)
            )
        )

    return ProductosResponse(
        nombre=random.choice(nombres),
        polizas=polizas
    )
