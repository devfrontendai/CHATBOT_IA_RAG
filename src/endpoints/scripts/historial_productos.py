from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token
import requests
from state import index

router = APIRouter()

OLLAMA_URL = "http://ollama:11434/api/generate"

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
                # Contexto RAG
                contexto = index.as_query_engine(similarity_top_k=6).query(data.pregunta)
                if not contexto or str(contexto).strip() == "":
                    respuesta = "No tengo información suficiente en la base proporcionada."
                    if data.session_id:
                        historial.append(Mensaje(content=respuesta, role="bot"))
                        save_history(data.session_id, historial)
                    return {"respuesta": respuesta}
                prompt = f"""
                Eres un asistente experto en productos de seguros.
                Debes enviar un script que resuma el historial de productos del asegurado.
                Debes hacer una sugerencia de algun producto que pueda interesarle al asegurado.
                Consulta la información del RAG para enriquecer tu respuesta.
                -----------------
                INFORMACIÓN DEL RAG:
                {contexto}
                -----------------
                Responde SIEMPRE en ESPAÑOL, en formato markdown (puedes usar listas o tablas).
                Si la información no está disponible, di: 'No tengo información suficiente en la base proporcionada.'
                Al FINAL sugiere amablemente una pregunta relevante para continuar la conversación.
                """
                payload = {
                    "model": "llama3:8b-instruct-q2_K",
                    "prompt": prompt,
                    "stream": False
                }
                response = requests.post(OLLAMA_URL, json=payload)
                response.raise_for_status()
                result = response.json()
                respuesta = result.get("response")
                if not respuesta:
                    respuesta = f"Tienes {len(historial)} productos: " + \
                        ", ".join([f"{h.producto} ({h.plan}, {h.estatus})" for h in historial])
                return HistorialProductosResponse(
                    nombre=data.get("name"),
                    historial_productos=historial,
                    script=respuesta if respuesta else "No se generó un script."
                )
            else:
                raise HTTPException(status_code=404, detail="No se encontró información de póliza")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
