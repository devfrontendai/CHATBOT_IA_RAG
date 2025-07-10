from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token

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

# Modelos de respuesta
class ProductoHistorial(BaseModel):
    producto: str
    plan: str
    estatus: str
    motivo_cancelacion: Optional[str] = None
    fecha_cancelacion: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None

class SugerenciaProducto(BaseModel):
    producto: str
    plan: str
    razon: str

class HistorialProductosResponse(BaseModel):
    nombre: str
    historial: List[ProductoHistorial]
    sugerencias: List[SugerenciaProducto]

@router.get("/historial_productos/{asegurado_id}", response_model=HistorialProductosResponse)
def historial_productos(
    asegurado_id: str,
    token: str = Depends(get_bearer_token)
):
    """
    Devuelve historial de productos del asegurado y sugerencias personalizadas (dummy).
    """
    # Aquí consumir el endpoint real (y el rag para agregar sugerencias)
    return HistorialProductosResponse(
        nombre=HISTORIAL_DUMMY["nombre"],
        historial=[ProductoHistorial(**h) for h in HISTORIAL_DUMMY["historial"]],
        sugerencias=[SugerenciaProducto(**s) for s in HISTORIAL_DUMMY["sugerencias"]]
    )
