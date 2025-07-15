from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.auth_utils import get_bearer_token
from utils.llm_utils import consultar_llm
import requests
from datetime import datetime

router = APIRouter()

class VigenciaPoliza(BaseModel):
    numero: str
    producto: str
    nombre_producto: Optional[str] = None
    plan: Optional[str] = None
    inicio_vigencia: str
    fin_vigencia: str

class ProximasVigenciasResponse(BaseModel):
    nombre: str
    proximas_vigencias: List[VigenciaPoliza]
    script: Optional[str] = None

def dias_restantes(fin_vigencia: str) -> Optional[int]:
    try:
        fecha_fin = datetime.strptime(fin_vigencia, "%Y-%m-%d")
        hoy = datetime.now()
        return (fecha_fin - hoy).days
    except Exception:
        return None

@router.get("/proximas_vigencias/{asegurado_id}", response_model=ProximasVigenciasResponse)
def proximas_vigencias(
    asegurado_id: str,
    token: str = Depends(get_bearer_token),
    nombre: str = None
):
    """
    Devuelve pólizas vigentes próximas a vencer, y una sugerencia/resumen generado por IA.
    Todas las pólizas retornadas son vigentes.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"https://amex-middleware-dev.insuranceservices.mx/api/v1/aramis/ia/policies/{asegurado_id}",
            headers=headers,
            timeout=15
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        polizas = data.get("policies") or []
        nombre_resp = data.get("name", nombre or "Asegurado")

        proximas_vigencias = []
        para_prompt = []

        UMBRAL_DIAS = 30  # Cambia aquí si quieres otro rango

        for p in polizas:
            fin_vig = p.get("fecha_fin_vigencia")
            dias = dias_restantes(fin_vig)
            if dias is not None and dias <= UMBRAL_DIAS:
                pol = VigenciaPoliza(
                    numero=str(p.get("numero", "")),
                    producto=p.get("producto", ""),
                    nombre_producto=p.get("nombre_producto", ""),
                    plan=p.get("nombre_plan", ""),
                    inicio_vigencia=p.get("fecha_inicio_vigencia", ""),
                    fin_vigencia=fin_vig
                )
                proximas_vigencias.append(pol)
                para_prompt.append(
                    f"- {pol.nombre_producto or pol.producto} (Póliza {pol.numero}): termina el {pol.fin_vigencia} (faltan {dias} días)"
                )

        # Prompt para el LLM
        resumen_str = "\n".join(para_prompt) if para_prompt else "No hay pólizas próximas a vencer."
        prompt = (
            f"Lista de pólizas próximas a vencer:\n{resumen_str}\n\n"
            "Por favor genera un resumen profesional en español para notificar al asegurado cuáles de sus pólizas están por expirar (menos de 30 días). "
            "Incluye producto, número de póliza y fecha de vencimiento. Si no hay ninguna próxima a expirar, solo dilo de forma clara."
        )

        script = consultar_llm(prompt)
        if not script or not isinstance(script, str):
            script = "No se pudo generar el resumen en este momento."

        return ProximasVigenciasResponse(
            nombre=nombre_resp,
            proximas_vigencias=proximas_vigencias,
            script=script
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
