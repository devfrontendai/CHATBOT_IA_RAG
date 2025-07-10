from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from utils.auth_utils import get_bearer_token

router = APIRouter()

# Dummy de próximas vigencias
VIGENCIAS_DUMMY = {
    "nombre": "Alfredo Tiprotec",
    "polizas_proximas_a_vencer": [
        {
            "producto": "GUARD FAMILY",
            "plan": "INDIVIDUAL ELITE",
            "numero": "9044140",
            "fecha_fin": "2024-07-10",  # Simula que vence pronto
            "dias_restantes": 5
        }
    ]
}

# Modelos de respuesta
class PolizaVigencia(BaseModel):
    producto: str
    plan: str
    numero: str
    fecha_fin: str
    dias_restantes: int

class VigenciasResponse(BaseModel):
    nombre: str
    polizas_proximas_a_vencer: List[PolizaVigencia]

@router.get("/vigencias/{asegurado_id}", response_model=VigenciasResponse)
def proxima_vigencia(
    asegurado_id: str,
    token: str = Depends(get_bearer_token)
):
    """
    Devuelve las pólizas vigentes próximas a vencer para el asegurado (dummy).
    """
    # Aquí iría la llamada real al back de Laravel
    return VigenciasResponse(
        nombre=VIGENCIAS_DUMMY["nombre"],
        polizas_proximas_a_vencer=[
            PolizaVigencia(**p) for p in VIGENCIAS_DUMMY["polizas_proximas_a_vencer"]
        ]
    )
