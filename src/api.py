from fastapi import APIRouter
from pydantic import BaseModel
import requests
from state import index

router = APIRouter()

OLLAMA_URL = "http://ollama:11434/api/generate"

class Mensaje(BaseModel):
    role: str
    content: str

class Pregunta(BaseModel):
    pregunta: str
    historial: list[Mensaje] = []

@router.post("/preguntar")
def preguntar(data: Pregunta):
    if index is None:
        return {"error": "El index aún no está listo, espera unos segundos y vuelve a intentar."}
    
    # Prepara historial como texto markdown para el prompt
    historial_txt = ""
    for m in data.historial:
        if m.role == "user":
            historial_txt += f"\n**Operador:** {m.content}\n"
        else:
            historial_txt += f"\n**Bot:** {m.content}\n"

    # Recupera contexto relevante del RAG
    contexto = index.as_query_engine(similarity_top_k=3).query(data.pregunta)
    
    # Si no hay contexto relevante, responde sin consultar al modelo
    if not contexto or str(contexto).strip() == "":
        return {"respuesta": "No tengo información suficiente en la base proporcionada."}
    
    # Construye el prompt con historial, contexto, y la pregunta actual
    prompt = f"""
    Eres un asistente para agentes de seguros, responde SOLO usando la siguiente información sobre productos, planes y coberturas (no inventes datos):

    ### Historial de la conversación
    {historial_txt}

    ### Datos relevantes encontrados
    {contexto}

    ### Pregunta del operador
    {data.pregunta}

    SIEMPRE responde en ESPAÑOL y en formato markdown (usa viñetas, negritas, tablas si aplica). Si no encuentras información, di: 'No tengo información suficiente en la base proporcionada.'
    """

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
        return {"respuesta": result.get("response")}
    except Exception as e:
        return {"error": str(e)}
