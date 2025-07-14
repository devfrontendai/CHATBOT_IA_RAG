from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List
import json
import os
from datetime import datetime
from .models import LogEntry, LogFilter 

router = APIRouter()
LOG_FILE = "logs/rag_logs.jsonl"

def filter_logs(
    logs: List[dict],
    operador: Optional[str],
    session_id: Optional[str],
    fecha_inicio: Optional[str],
    fecha_fin: Optional[str]
):
    # Filtra por operador, session_id y fecha (timestamp)
    if operador:
        logs = [l for l in logs if str(l.get("operador")) == operador]
    if session_id:
        logs = [l for l in logs if str(l.get("session_id")) == session_id]
    if fecha_inicio:
        start_ts = datetime.fromisoformat(fecha_inicio).timestamp()
        logs = [l for l in logs if l.get("timestamp", 0) >= start_ts]
    if fecha_fin:
        end_ts = datetime.fromisoformat(fecha_fin).timestamp()
        logs = [l for l in logs if l.get("timestamp", 0) <= end_ts]
    return logs

@router.get("/logs", response_model=dict)
def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    operador: Optional[str] = None,
    session_id: Optional[str] = None,
    fecha_inicio: Optional[str] = None,  # formato: "2025-07-13T00:00:00"
    fecha_fin: Optional[str] = None
):
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="No log file found")
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except Exception:
                pass

    logs = filter_logs(logs, operador, session_id, fecha_inicio, fecha_fin)
    total = len(logs)
    start = (page - 1) * page_size
    end = start + page_size
    page_logs = logs[start:end]
    # Usa LogEntry para tipar la respuesta
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "logs": [LogEntry(**log) for log in page_logs]
    }

@router.post("/logs/query", response_model=dict)
def query_logs(filters: LogFilter):
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="No log file found")
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except Exception:
                pass

    logs = filter_logs(logs, filters.operador, filters.session_id, filters.fecha_inicio, filters.fecha_fin)
    total = len(logs)
    start = (filters.page - 1) * filters.page_size
    end = start + filters.page_size
    page_logs = logs[start:end]
    return {
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "logs": [LogEntry(**log) for log in page_logs]
    }

@router.get("/logs/download")
def download_logs():
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="No log file found")
    return FileResponse(LOG_FILE, media_type="application/octet-stream", filename="rag_logs.jsonl")
