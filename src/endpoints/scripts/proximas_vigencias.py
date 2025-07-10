from fastapi import APIRouter
from typing import List

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

@router.get("/proximas_vigencias")
def proximas_vigencias(nombre: str = None):
    """
    Devuelve pólizas vigentes próximas a vencer (dummy).
    """
    # Aquí después consumes el endpoint real de Laravel, filtras vigentes y próximas a vencer
    return {
        "nombre": nombre or "Asegurado Dummy",
        "proximas_vigencias": PROXIMAS_VIGENCIAS_DUMMY
    }
