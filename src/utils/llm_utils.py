import os
import requests
from state import index

def consultar_llm_ollama(prompt: str) -> str:
    """
    Consulta el modelo local Ollama vía llama_index.
    """
    try:
        if index is None:
            return "El modelo local aún no está listo."
        contexto = index.as_query_engine(similarity_top_k=6).query(prompt)
        return str(contexto) if contexto else "No tengo sugerencias suficientes."
    except Exception as e:
        return f"[OLLAMA ERROR]: {e}"

def consultar_llm_openai(prompt: str) -> str:
    """
    Consulta el modelo OpenAI vía API.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[OPENAI ERROR]: No hay API key configurada."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 350
    }
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        return f"[OPENAI ERROR]: {data}"
    except Exception as e:
        return f"[OPENAI ERROR]: {e}"

def consultar_llm_gemini(prompt: str) -> str:
    """
    Consulta Gemini (Google AI). Implementa aquí si tienes API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "[GEMINI ERROR]: No hay API key configurada."
    # Integración real aquí
    return "[GEMINI]: (integración pendiente)"

def consultar_llm(prompt: str) -> str:
    """
    Decide a qué modelo LLM llamar (Ollama, OpenAI, Gemini), según variable de entorno.
    Prioridad: OpenAI > Gemini > Ollama (local).
    """
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
    use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"

    if use_openai:
        return consultar_llm_openai(prompt)
    elif use_gemini:
        return consultar_llm_gemini(prompt)
    elif use_ollama:
        return consultar_llm_ollama(prompt)
    else:
        return "No hay ningún modelo LLM habilitado."

