from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token
from utils.llm_utils import consultar_llm
from utils.token_utils import calcular_tokens_y_costo  # <---
import requests

router = APIRouter()

class PolizaCancelada(BaseModel):
    numero: str
    producto: str
    plan: str
    motivo_cancelacion: str
    fecha_cancelacion: str
    nombre_producto: Optional[str] = None
    nombre_plan: Optional[str] = None

class CanceladasResponse(BaseModel):
    nombre: str
    canceladas: List[PolizaCancelada]
    script: Optional[str] = None
    tokens_usados: Optional[dict] = None  # <---

@router.get("/polizas_canceladas/{asegurado_id}", response_model=CanceladasResponse)
def polizas_canceladas(
    asegurado_id: str,
    token: str = Depends(get_bearer_token),
    nombre: str = None
):
    """
    Devuelve todas las pólizas canceladas del asegurado y un resumen generado por IA.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"https://amex-middleware-dev.insuranceservices.mx/api/v1/aramis/ia/cancelled-policies/{asegurado_id}",
            headers=headers,
            timeout=15
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        polizas = data.get("policies") or []
        nombre_resp = data.get("name", nombre or "Asegurado")

        canceladas = []
        resumen_items = []
        for p in polizas:
            poliza = PolizaCancelada(
                numero=str(p.get("numero", "")),
                producto=p.get("producto", ""),
                plan=p.get("plan", ""),
                motivo_cancelacion=p.get("motivo_cancelacion", ""),
                fecha_cancelacion=p.get("fecha_cancelacion", ""),
                nombre_producto=p.get("nombre_producto", ""),
                nombre_plan=p.get("nombre_plan", "")
            )
            canceladas.append(poliza)
            if poliza.motivo_cancelacion and poliza.fecha_cancelacion:
                resumen_items.append(f"- Póliza **{poliza.numero}** cancelada el {poliza.fecha_cancelacion} por motivo: _{poliza.motivo_cancelacion}_")

        resumen_str = "\n".join(resumen_items) if resumen_items else "No se encontraron pólizas canceladas con fecha y motivo."
        prompt = (
            f"Lista de pólizas canceladas:\n{resumen_str}\n\n"
            "Por favor genera un resumen breve y profesional en español indicando las fechas y motivos principales de cancelación para reportar al usuario. "
            "Responde solo el resumen, en lenguaje claro."
        )
        resumen_ia = consultar_llm(prompt)
        if not resumen_ia or not isinstance(resumen_ia, str):
            resumen_ia = "No se pudo generar el resumen en este momento."
        
        tokens_info = calcular_tokens_y_costo(prompt, resumen_ia)

        return CanceladasResponse(
            nombre=nombre_resp,
            canceladas=canceladas,
            script=resumen_ia,
            tokens_usados=tokens_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
