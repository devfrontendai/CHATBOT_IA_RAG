from fastapi import APIRouter
from pydantic import BaseModel
from utils.log_utils import log_rag_feedback

router = APIRouter()

class FeedbackInput(BaseModel):
    session_id: str
    pregunta: str
    respuesta: str
    utilidad: int
    comentario: str | None = None

@router.post("/feedback")
def feedback(data: FeedbackInput):
    log_rag_feedback(data)
    return {"ok": True}
