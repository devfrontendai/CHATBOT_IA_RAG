from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token
import requests

router = APIRouter()

# Dummy para fallback
HISTORIAL_DUMMY = {
    "nombre": "Alfredo Tiprotec",
    "historial_productos": [
        {
            "producto": "TRAVEL ANNUAL 4.0",
            "plan": "FAMILIAR ADVANCED",
            "estatus": "Cancelada"
        },
        {
            "producto": "GUARD FAMILY",
            "plan": "INDIVIDUAL ELITE",
            "estatus": "Vigente"
        }
    ]
}

class ProductoHistorial(BaseModel):
    producto: str
    plan: Optional[str] = None
    estatus: str
    motivo_cancelacion: Optional[str] = None
    fecha_cancelacion: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None

class HistorialProductosResponse(BaseModel):
    nombre: str
    historial_productos: List[ProductoHistorial]

@router.get("/historial_productos/{asegurado_id}", response_model=HistorialProductosResponse)
def historial_productos(
    asegurado_id: str,
    token: str = Depends(get_bearer_token)
):
    """
    Devuelve historial de productos del asegurado (real o dummy).
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"https://amex-middleware-dev.insuranceservices.mx/api/v1/aramis/ia/policies/{asegurado_id}",
            headers=headers,
            timeout=8
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("polices"):
                historial = []
                p = data["polices"]
                historial.append(ProductoHistorial(
                    producto=p.get("nombre_producto"),
                    plan=p.get("nombre_plan"),
                    estatus=p.get("estatus")
                ))
                return HistorialProductosResponse(
                    nombre=data.get("name"),
                    historial_productos=historial
                )
            else:
                raise HTTPException(status_code=404, detail="No se encontró información de póliza")
        else:
            raise HTTPException(status_code=response.status_code, detail="Error al consultar pólizas"
        Fallback dummy (elimina esto cuando uses el endpoint real)
        return HistorialProductosResponse(
            nombre=HISTORIAL_DUMMY["nombre"],
            historial_productos=[
                ProductoHistorial(**h) for h in HISTORIAL_DUMMY["historial_productos"]
            ]
        )
    except Exception as e:
        # Fallback dummy en caso de error
        return HistorialProductosResponse(
            nombre=HISTORIAL_DUMMY["nombre"],
            historial_productos=[
                ProductoHistorial(**h) for h in HISTORIAL_DUMMY["historial_productos"]
            ]
        )
