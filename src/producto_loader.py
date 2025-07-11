from llama_index.core import Document
import json

def load_productos(path="info/productos.json"):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    productos = data if isinstance(data, list) else data["productos"]
    documents = []
    for p in productos:
        for plan in p.get("planes", []):
            cob = plan.get("coberturas", [])
            textos = [c["fc_cobertura"] for c in cob]
            texto = (
                f"Producto {p['fc_numero_producto']} - {p['fc_descripcion_producto']}\n"
                f"Aseguradora: {p.get('fc_descripcion_aseguradora', 'Desconocida')}\n"
                f"Plan: {plan.get('fc_descripcion_plan')}\n"
                f"Coberturas: {', '.join(textos) if textos else 'Ninguna'}\n"
            )
            documents.append(Document(text=texto, metadata={
                "numero_producto": p["fc_numero_producto"],
                "plan": plan.get('fc_descripcion_plan', '')
            }))
    return documents

def load_faqs(path="info/faqs.json"):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    documents = []
    for faq in data:
        text = f"Pregunta frecuente: {faq['pregunta']}\nRespuesta: {faq['respuesta']}"
        documents.append(Document(
            text=text,
            metadata={"tipo": "faq", "pregunta": faq["pregunta"]}
        ))
    return documents
