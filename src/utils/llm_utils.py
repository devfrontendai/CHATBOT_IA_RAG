import os
from state import index

def consultar_llm_ollama(prompt: str) -> str:
    if index is None:
        return "El modelo aún no está listo, espera unos segundos y vuelve a intentar."
    contexto = index.as_query_engine(similarity_top_k=6).query(prompt)
    return str(contexto) if contexto else "No tengo sugerencias suficientes."

def consultar_llm_openai(prompt: str) -> str:
    import requests
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    if not api_key:
        return "No hay API key de OpenAI configurada."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 350
    }
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
    data = resp.json()
    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    return "No se pudo obtener sugerencia del modelo OpenAI."

def consultar_llm_gemini(prompt: str) -> str:
    import requests
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "No hay API key de Gemini configurada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    resp = requests.post(url, json=payload, timeout=20)
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "No se pudo obtener sugerencia del modelo Gemini."

def consultar_llm(prompt: str) -> str:
    backend = os.getenv("LLM_BACKEND", "ollama").lower()
    if backend == "openai":
        return consultar_llm_openai(prompt)
    if backend == "gemini":
        return consultar_llm_gemini(prompt)
    # Default: Ollama
    return consultar_llm_ollama(prompt)
