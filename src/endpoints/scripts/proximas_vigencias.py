from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from utils.auth_utils import get_bearer_token

router = APIRouter()

# Dummy
PROXIMAS_VIGENCIAS_DUMMY = [
    {
        "numero": "5550001",
        "producto": "SAFE TRAVEL",
        "plan": "FAMILIAR BASIC",
        "inicio_vigencia": "2024-07-10",
        "fin_vigencia": "2024-07-15"
    },
    {
        "numero": "5550002",
        "producto": "GUARD FAMILY",
        "plan": "INDIVIDUAL ELITE",
        "inicio_vigencia": "2024-07-01",
        "fin_vigencia": "2024-07-13"
    }
]

class VigenciaPoliza(BaseModel):
    numero: str
    producto: str
    plan: str
    inicio_vigencia: str
    fin_vigencia: str

class ProximasVigenciasResponse(BaseModel):
    nombre: str
    proximas_vigencias: List[VigenciaPoliza]

@router.get("/proximas_vigencias/{asegurado_id}", response_model=ProximasVigenciasResponse)
def proximas_vigencias(
    asegurado_id: str,
    token: str = Depends(get_bearer_token),
    nombre: str = None
):
    """
    Devuelve pólizas vigentes próximas a vencer (dummy).
    """
    # Endpoint
    return ProximasVigenciasResponse(
        nombre=nombre or "Asegurado Dummy",
        proximas_vigencias=[VigenciaPoliza(**v) for v in PROXIMAS_VIGENCIAS_DUMMY]
    )
