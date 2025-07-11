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
    ],
    "script": "Tienes 2 productos, uno con estatus cancelado y otro con estatus vigente."
}

class ProductoHistorial(BaseModel):
    producto: str
    plan: str
    estatus: str
    motivo_cancelacion: Optional[str] = None

class HistorialProductosResponse(BaseModel):
    nombre: str
    historial_productos: List[ProductoHistorial]
    script: Optional[str] = None

def traducir_estatus(estatus):
    if estatus is None:
        return ""
    estatus = str(estatus).upper()
    if estatus == "C":
        return "Cancelada"
    if estatus == "V":
        return "Vigente"
    return estatus

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
            polizas = data.get("policies") or data.get("polices")
            if polizas and isinstance(polizas, list):
                historial = []
                for p in polizas:
                    motivo = p.get("motivo_cancelacion")
                    motivo_str = str(motivo) if motivo not in [None, ""] else None
                    historial.append(ProductoHistorial(
                        producto=p.get("nombre_producto"),
                        plan=p.get("nombre_plan"),
                        estatus=traducir_estatus(p.get("estatus")),
                        motivo_cancelacion=motivo_str
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
