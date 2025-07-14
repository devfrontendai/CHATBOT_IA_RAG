from fastapi import APIRouter
from pydantic import BaseModel
from utils.cache_utils import rdb

router = APIRouter()

def clear_active_session(operator_id: str):
    key = f"chat:agente:{operator_id}"
    rdb.delete(key)

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
