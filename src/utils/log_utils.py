import json
import time
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def safe_string(obj):
    try:
        return str(obj)
    except Exception:
        return repr(obj)

def log_rag_interaction(session_id, pregunta, contexto, respuesta, operador):
    log = {
        "timestamp": time.time(),
        "session_id": str(session_id) if session_id is not None else "",
        "pregunta": str(pregunta) if pregunta is not None else "",
        "contexto": safe_string(contexto),
        "respuesta": str(respuesta) if respuesta is not None else "",
        "operador": str(operador) if operador is not None else "",
    }
    with open(os.path.join(LOG_DIR, "rag_logs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
