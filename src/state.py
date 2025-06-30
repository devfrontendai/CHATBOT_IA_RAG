from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
Settings.llm = Ollama(
    model="gemma3:1b",
    base_url="http://ollama:11434",  # <--- esto es CRÍTICO
    request_timeout=300
)

from llama_index.core import StorageContext, load_index_from_storage

persist_dir = "storage"
storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
index = load_index_from_storage(storage_context)
