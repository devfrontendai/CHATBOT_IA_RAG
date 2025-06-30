from fastapi import APIRouter
from pydantic import BaseModel
import requests
from state import index

router = APIRouter()

OLLAMA_URL = "http://ollama:11434/api/generate"

class Pregunta(BaseModel):
    pregunta: str

@router.post("/preguntar")
def preguntar(data: Pregunta):
    if index is None:
        return {"error": "El index aún no está listo, espera unos segundos y vuelve a intentar."}
    
    # Recupera contexto del index (puedes ajustar similarity_top_k si necesitas más info)
    contexto = index.as_query_engine(similarity_top_k=3).query(data.pregunta)
    
    # Si no hay contexto relevante, responde sin consultar al modelo
    if not contexto or str(contexto).strip() == "":
        return {"respuesta": "No tengo información suficiente en la base proporcionada."}
    
    prompt = f"""
    Responde SOLO usando la siguiente información sobre productos, planes y coberturas, sin inventar datos.
    Responde SIEMPRE en español, sin mezclar inglés.
    La respuesta debe ser clara y en máximo 4 líneas, formato texto plano, sin saltos de línea innecesarios, sin /n, sin viñetas, solo un párrafo continuo y fácil de leer. No escribas en formato lista ni HTML.
    -----
    {contexto}
    -----
    Pregunta del usuario: {data.pregunta}
    Si no encuentras información en los datos, di: 'No tengo información suficiente en la base proporcionada.'
    """

    # (opcional) print para debug
    print("=== CONTEXTO ENVIADO AL MODELO ===\n", contexto)
    print("=== PROMPT COMPLETO ===\n", prompt)
    
    payload = {
        "model": "gemma3:1b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        # (opcional) Devuelve también el contexto para debug, quita esta línea en producción
        return {
            "respuesta": result.get("response"),
            # "contexto_usado": contexto  # quita esta línea si no quieres mostrar el contexto en la respuesta
        }
    except Exception as e:
        return {"error": str(e)}
