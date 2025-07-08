from producto_loader import load_productos, load_faqs
from rag_engine import build_index
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_community.llms import Ollama
import os

if not os.path.exists("storage"):
    os.makedirs("storage")

print("🔄 Cargando productos y FAQs...")
productos_docs = load_productos("info/productos.json")
faqs_docs = load_faqs("info/faqs.json")
all_docs = productos_docs + faqs_docs
print(f"✅ Documentos cargados: {len(all_docs)}")

print("🔄 Inicializando embedding y modelo...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
llm = Ollama(model="gemma3:1b")

print("🔄 Construyendo el índice vectorial...")
index = build_index(all_docs, embed_model, llm)

print("💾 Guardando índice en disco (storage/)...")
index.storage_context.persist(persist_dir="storage")
print("✅ ¡Index guardado listo para usar!")
