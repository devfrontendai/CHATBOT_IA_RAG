from fastapi import APIRouter
from typing import List

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

@router.get("/polizas_canceladas")
def polizas_canceladas(nombre: str = None):
    """
    Devuelve todas las pólizas canceladas del asegurado (dummy).
    """
    # polizas = requests.get(f"http://tu-back/asegurado/polizas?nombre={nombre}").json()["polizas"]
    # return [p for p in polizas if p["estatus"] == "Cancelada"]
    return {
        "nombre": nombre or "Asegurado Dummy",
        "canceladas": CANCELADAS_DUMMY
    }
