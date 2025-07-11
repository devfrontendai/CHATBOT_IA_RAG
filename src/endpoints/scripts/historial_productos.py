from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from utils.auth_utils import get_bearer_token
import requests

router = APIRouter()

class ProductoHistorial(BaseModel):
    producto: str
    plan: str
    estatus: str
    motivo_cancelacion: str = None

class HistorialProductosResponse(BaseModel):
    nombre: str
    historial_productos: List[ProductoHistorial]
    script: str

def traducir_estatus(e):
    return {
        "C": "Cancelada",
        "V": "Vigente"
    }.get(e, e)

@router.get("/historial_productos/{asegurado_id}", response_model=HistorialProductosResponse)
def historial_productos(
    asegurado_id: str,
    token: str = Depends(get_bearer_token)
):
    """
    Devuelve historial de productos del asegurado.
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
            if data.get("policies"):
                historial = []
                for p in data["policies"]:
                    historial.append(ProductoHistorial(
                        producto=p.get("nombre_producto"),
                        plan=p.get("nombre_plan"),
                        estatus=traducir_estatus(p.get("estatus")),
                        motivo_cancelacion=p.get("motivo_cancelacion")
                    ))
                script = f"Tienes {len(historial)} productos: " + \
                         ", ".join([f"{h.producto} ({h.plan}, {h.estatus})" for h in historial])
                return HistorialProductosResponse(
                    nombre=data.get("name"),
                    historial_productos=historial,
                    script=script
                )
            else:
                raise HTTPException(status_code=404, detail="No se encontró información de póliza")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
