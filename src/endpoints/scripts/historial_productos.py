from fastapi import APIRouter
from typing import List

router = APIRouter()

# Dummy de historial de productos y sugerencias
HISTORIAL_DUMMY = {
    "nombre": "Alfredo Tiprotec",
    "historial": [
        {
            "producto": "TRAVEL ANNUAL 4.0",
            "plan": "FAMILIAR ADVANCED",
            "estatus": "Cancelada",
            "motivo_cancelacion": "DUPLICIDAD POLIZA",
            "fecha_cancelacion": "2025-05-06"
        },
        {
            "producto": "GUARD FAMILY",
            "plan": "INDIVIDUAL ELITE",
            "estatus": "Vigente",
            "fecha_inicio": "2025-06-01",
            "fecha_fin": "2026-06-01"
        }
    ],
    "sugerencias": [
        {
            "producto": "GUARD FAMILY",
            "plan": "FAMILIAR PREMIUM",
            "razon": "Basado en tu historial y vigencias, este producto te ofrece mayor cobertura familiar."
        },
        {
            "producto": "TRAVEL ANNUAL 5.0",
            "plan": "INDIVIDUAL ELITE",
            "razon": "Nueva versión disponible, mayor cobertura internacional."
        }
    ]
}

@router.get("/historial_productos")
def historial_productos(nombre: str = None):
    """
    Devuelve historial de productos del asegurado y sugerencias personalizadas (dummy).
    """
    # Aquí consumir el endpoint real (y el rag para agregar sugerencias)
    return {
        "nombre": nombre or HISTORIAL_DUMMY["nombre"],
        "historial": HISTORIAL_DUMMY["historial"],
        "sugerencias": HISTORIAL_DUMMY["sugerencias"]
    }
