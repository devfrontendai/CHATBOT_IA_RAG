from pydantic import BaseModel
from typing import Optional

class LogEntry(BaseModel):
    timestamp: float
    session_id: Optional[str]
    pregunta: Optional[str]
    contexto: Optional[str]
    respuesta: Optional[str]
    operador: Optional[str]

class LogFilter(BaseModel):
    page: int = 1
    page_size: int = 20
    operador: Optional[str] = None
    session_id: Optional[str] = None
    fecha_inicio: Optional[str] = None  # formato: "2025-07-13T00:00:00"
    fecha_fin: Optional[str] = None
