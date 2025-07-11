from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token
import requests
from state import index

router = APIRouter()

# ... (Modelos y dummy igual que antes)

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

                # ---- Prompt para el RAG ----
                productos_str = ", ".join(set(filter(None, productos_lista)))
                prompt = f"""
                El asegurado ya tiene estos productos: {productos_str}.
                NO RECOMIENDES ningún producto ni plan igual a los que ya tiene. Recomienda solo productos diferentes o upgrades. 
                Si no hay opciones mejores, responde: 'No hay sugerencias de productos adicionales para el portafolio actual.'
                Explica brevemente tu sugerencia en español.
                """
                # --- Llamada al RAG/modelo ---
                rag_result = index.as_query_engine(similarity_top_k=6).query(prompt)
                respuesta = rag_result.response if hasattr(rag_result, "response") else str(rag_result)
                respuesta_lower = respuesta.lower()

                # --- Filtro: si sugiere producto ya adquirido, reemplaza ---
                ya_tiene = set(prod.lower() for prod in productos_lista if prod)
                sugerido = False
                for prod in ya_tiene:
                    if prod and prod in respuesta_lower:
                        sugerido = True
                        break

                if sugerido:
                    respuesta = "No hay sugerencias de productos adicionales para el portafolio actual."

                return HistorialProductosResponse(
                    nombre=data.get("name"),
                    historial_productos=historial,
                    script=respuesta
                )
            else:
                raise HTTPException(status_code=404, detail="No se encontró información de póliza")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
