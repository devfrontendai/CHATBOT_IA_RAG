from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import redis
import json
from state import index

router = APIRouter()

OLLAMA_URL = "http://ollama:11434/api/generate"
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0

# Redis connection
rdb = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

class Mensaje(BaseModel):
    content: str
    role: str  # "user" o "bot"

class Pregunta(BaseModel):
    pregunta: str
    historial: list[Mensaje] = []
    session_id: str | None = None
    operator_id: str | None = None

MAX_HISTORY = 10

def save_history(session_id: str, historial: list[Mensaje]):
    key = f"chat:historial:{session_id}"
    data = json.dumps([m.dict() for m in historial[-MAX_HISTORY:]])
    rdb.set(key, data, ex=60*60)  # TTL: 1h

def load_history(session_id: str) -> list[Mensaje]:
    key = f"chat:historial:{session_id}"
    data = rdb.get(key)
    if data:
        return [Mensaje(**x) for x in json.loads(data)]
    return []

def set_active_session(operator_id: str, session_id: str):
    key = f"chat:agente:{operator_id}"
    rdb.set(key, session_id, ex=3600)

def get_active_session(operator_id: str) -> str | None:
    key = f"chat:agente:{operator_id}"
    return rdb.get(key)

def clear_active_session(operator_id: str):
    key = f"chat:agente:{operator_id}"
    rdb.delete(key)

def resumen_historial(historial):
    if not historial:
        return ""
    ultimos_turnos = historial[-2:]
    texto = ""
    for m in ultimos_turnos:
        rol = "Usuario" if m.role == "user" else "Asistente"
        texto += f"{rol}: {m.content}\n"
    return texto

@router.post("/preguntar")
def preguntar(data: Pregunta):
    if index is None:
        return {"respuesta": "El index aún no está listo, espera unos segundos y vuelve a intentar."}

    # --- Controla sesiones duplicadas ---
    if data.operator_id and data.session_id:
        current_session = get_active_session(data.operator_id)
        if current_session and current_session != data.session_id:
            return {
                "respuesta": (
                    f"Ya hay un agente con el id {data.operator_id} activo en otra sala de chat, espera a que termine."
                )
            }
        set_active_session(data.operator_id, data.session_id)

    # --- HISTORIAL REDIS ---
    if data.session_id:
        historial = load_history(data.session_id)
        historial.append(Mensaje(content=data.pregunta, role="user"))
    else:
        historial = data.historial[-MAX_HISTORY:]

    texto_historial = resumen_historial(historial)
    for m in historial[-MAX_HISTORY:]:
        rol = "Usuario" if m.role == "user" else "Asistente"
        texto_historial += f"{rol}: {m.content}\n"

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
    Toma en cuenta la conversación previa, pero SI el usuario pregunta por un producto o plan diferente, olvida temas previos y responde solo de lo actual.

    Conversación previa:
    {texto_historial}

    -----------------
    INFORMACIÓN DEL RAG:
    {contexto}
    -----------------

    Responde SIEMPRE en ESPAÑOL, en formato markdown (puedes usar listas o tablas).
    Si la información no está disponible, di: 'No tengo información suficiente en la base proporcionada.'
    Al FINAL sugiere amablemente una pregunta relevante para continuar la conversación.
    """

    print("=== HISTORIAL ===\n", texto_historial)
    print("=== CONTEXTO ENVIADO AL MODELO ===\n", contexto)
    print("=== PROMPT COMPLETO ===\n", prompt)

    payload = {
        "model": "llama3:8b-instruct-q2_K",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        respuesta = result.get("response")
        if data.session_id:
            historial.append(Mensaje(content=respuesta, role="bot"))
            save_history(data.session_id, historial)
        return {"respuesta": respuesta}
    except Exception as e:
        return {"error": str(e)}

class FinalizarSesionInput(BaseModel):
    session_id: str
    operator_id: str | None = None

@router.post("/finalizar_sesion")
def finalizar_sesion(data: FinalizarSesionInput):
    key = f"chat:historial:{data.session_id}"
    rdb.delete(key)
    if data.operator_id:
        clear_active_session(data.operator_id)
    return {"ok": True, "msg": "Sesión finalizada y memoria eliminada"}
