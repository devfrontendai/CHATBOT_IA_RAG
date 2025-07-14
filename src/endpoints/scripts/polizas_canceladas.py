from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from utils.auth_utils import get_bearer_token
import requests
import json

router = APIRouter()

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
    Devuelve todas las pólizas canceladas del asegurado.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"https://amex-middleware-dev.insuranceservices.mx/api/v1/aramis/ia/cancelled-policies/{asegurado_id}",
            headers=headers,
            timeout=8
        )
        print("Response STATUS:", response.status_code)
        print("Response TEXT:", response.text)
        try:
            data = response.json()
            print("Response JSON:", json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print("Error parsing JSON:", e)
            print("Response TEXT (fallback):", response.text)
            data = {}

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        polizas = data.get("canceladas") or data.get("polizas") or []
        nombre_resp = data.get("name", nombre or "Asegurado")

        canceladas = []
        for p in polizas:
            canceladas.append(PolizaCancelada(
                numero=str(p.get("numero", "")),
                producto=p.get("producto", ""),
                plan=p.get("plan", ""),
                motivo_cancelacion=str(p.get("motivo_cancelacion", "")),
                fecha_cancelacion=str(p.get("fecha_cancelacion", ""))
            ))

        return CanceladasResponse(
            nombre=nombre_resp,
            canceladas=canceladas
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
