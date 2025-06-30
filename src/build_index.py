# build_index.py
from producto_loader import load_productos
from rag_engine import build_index
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_community.llms import Ollama
from llama_index.core import StorageContext

import os

if not os.path.exists("storage"):
    os.makedirs("storage")

print("🔄 Cargando productos...")
documents = load_productos("info/productos.json")
print(f"✅ Productos cargados: {len(documents)}")

print("🔄 Inicializando embedding y modelo...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
llm = Ollama(model="gemma3:1b")

print("🔄 Construyendo el índice vectorial (esto sí puede tardar varios minutos)...")
index = build_index(documents, embed_model, llm)

print("💾 Guardando índice en disco (storage/)...")
index.storage_context.persist(persist_dir="storage")
print("✅ ¡Index guardado listo para usar!")
