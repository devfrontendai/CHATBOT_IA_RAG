from fastapi import APIRouter

router = APIRouter()

# Dummy de próximas vigencias
VIGENCIAS_DUMMY = {
    "nombre": "Alfredo Tiprotec",
    "polizas_proximas_a_vencer": [
        {
            "producto": "GUARD FAMILY",
            "plan": "INDIVIDUAL ELITE",
            "numero": "9044140",
            "fecha_fin": "2024-07-10",  # Simula que vence pronto
            "dias_restantes": 5
        }
    ]
}

@router.get("/vigencias")
def proxima_vigencia(nombre: str = None):
    """
    Devuelve las pólizas vigentes próximas a vencer para el asegurado (dummy).
    """
    # Endpoint real
    return {
        "nombre": nombre or VIGENCIAS_DUMMY["nombre"],
        "polizas_proximas_a_vencer": VIGENCIAS_DUMMY["polizas_proximas_a_vencer"]
    }
