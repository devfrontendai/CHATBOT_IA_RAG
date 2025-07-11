from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token
from utils.llm_utils import consultar_llm
import requests

router = APIRouter()

# ----- Modelos -----
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
    Devuelve historial de productos del asegurado y una sugerencia personalizada.
    Si falla la consulta, devuelve el error real (NO dummy).
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"https://amex-middleware-dev.insuranceservices.mx/api/v1/aramis/ia/policies/{asegurado_id}",
            headers=headers,
            timeout=8
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        polizas = data.get("policies") or data.get("polices")
        if not polizas or not isinstance(polizas, list) or len(polizas) == 0:
            raise HTTPException(status_code=404, detail="No se encontró información de póliza")

        historial = []
        productos_lista = []
        for p in polizas:
            motivo = p.get("motivo_cancelacion")
            motivo_str = str(motivo) if motivo not in [None, ""] else None
            historial.append(ProductoHistorial(
                producto=p.get("nombre_producto"),
                plan=p.get("nombre_plan"),
                estatus=traducir_estatus(p.get("estatus")),
                motivo_cancelacion=motivo_str
            ))
            productos_lista.append(p.get("nombre_producto"))

        # Prompt para LLM/RAG
        productos_str = ", ".join(sorted(set(filter(None, productos_lista))))
        prompt = (
            f"El asegurado ya tiene estos productos: {productos_str}.\n"
            "No repitas productos ni planes que ya posee. "
            "¿Qué producto o plan adicional (o upgrade) recomendarías para complementar o mejorar su portafolio?\n"
            "Justifica brevemente tu sugerencia con base en la información interna de productos de seguros.\n"
            "Responde SOLO con la sugerencia y la justificación, en español."
        )

        respuesta = consultar_llm(prompt)
        if not respuesta or not isinstance(respuesta, str):
            respuesta = "No se pudo obtener una sugerencia en este momento."

        return HistorialProductosResponse(
            nombre=data.get("name", "Asegurado"),
            historial_productos=historial,
            script=respuesta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
