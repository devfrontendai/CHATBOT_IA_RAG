import json
import time
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_rag_interaction(session_id, pregunta, contexto, respuesta, operador):
    log = {
        "timestamp": time.time(),
        "session_id": session_id,
        "pregunta": pregunta,
        "contexto": contexto,
        "respuesta": respuesta,
        "operador": operador
    }
    with open(os.path.join(LOG_DIR, "rag_logs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
