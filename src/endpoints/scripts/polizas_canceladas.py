from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from utils.auth_utils import get_bearer_token

router = APIRouter()

# Dummy de ejemplo (después conectas el endpoint real de Laravel)
CANCELADAS_DUMMY = [
    {
        "numero": "9044139",
        "producto": "TRAVEL ANNUAL 4.0",
        "plan": "FAMILIAR ADVANCED",
        "motivo_cancelacion": "DUPLICIDAD POLIZA",
        "fecha_cancelacion": "2025-05-06"
    },
    {
        "numero": "8765432",
        "producto": "GUARD FAMILY",
        "plan": "INDIVIDUAL ELITE",
        "motivo_cancelacion": "NO PAGO",
        "fecha_cancelacion": "2024-12-01"
    }
]

class PolizaCancelada(BaseModel):
    numero: str
    producto: str
    plan: str
    motivo_cancelacion: str
    fecha_cancelacion: str

class CanceladasResponse(BaseModel):
    nombre: str
    canceladas: List[PolizaCancelada]

@router.get("/polizas_canceladas/{asegurado_id}", response_model=CanceladasResponse)
def polizas_canceladas(
    asegurado_id: str,
    token: str = Depends(get_bearer_token),
    nombre: str = None
):
    """
    Devuelve todas las pólizas canceladas del asegurado (dummy).
    """
    # polizas = requests.get(f"http://tu-back/asegurado/polizas?nombre={nombre}").json()["polizas"]
    # return [p for p in polizas if p["estatus"] == "Cancelada"]
    return CanceladasResponse(
        nombre=nombre or "Asegurado Dummy",
        canceladas=[PolizaCancelada(**p) for p in CANCELADAS_DUMMY]
    )
