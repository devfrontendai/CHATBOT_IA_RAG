import os
import requests
from state import index

class LLMTimeout(Exception):
    pass

class LLMServiceError(Exception):
    pass

def consultar_llm_ollama(prompt: str) -> str:
    if index is None:
        raise LLMServiceError("El modelo aún no está listo, espera unos segundos y vuelve a intentar.")
    try:
        contexto = index.as_query_engine(similarity_top_k=6).query(prompt)
        return str(contexto) if contexto else "No tengo sugerencias suficientes."
    except Exception as e:
        raise LLMServiceError(f"Error consultando modelo Ollama: {str(e)}")

def consultar_llm_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    if not api_key:
        raise LLMServiceError("No hay API key de OpenAI configurada.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 350
    }
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        return "No se pudo obtener sugerencia del modelo OpenAI."
    except requests.Timeout:
        raise LLMTimeout("Timeout al consultar OpenAI")
    except Exception as e:
        raise LLMServiceError(f"Error consultando OpenAI: {str(e)}")

def consultar_llm_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMServiceError("No hay API key de Gemini configurada.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.Timeout:
        raise LLMTimeout("Timeout al consultar Gemini")
    except Exception as e:
        raise LLMServiceError(f"Error consultando Gemini: {str(e)}")

def consultar_llm(prompt: str) -> str:
    backend = os.getenv("LLM_BACKEND", "ollama").lower()
    if backend == "openai":
        return consultar_llm_openai(prompt)
    if backend == "gemini":
        return consultar_llm_gemini(prompt)
    # Default: Ollama
    return consultar_llm_ollama(prompt)
