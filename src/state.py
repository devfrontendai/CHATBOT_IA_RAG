import os
from dotenv import load_dotenv
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

# Embeddings
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "huggingface").lower()
if EMBEDDING_BACKEND == "openai":
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    Settings.embed_model = OpenAIEmbedding(api_key=openai_api_key, model=openai_embedding_model)
else:
    hf_embedding_model = os.getenv("HF_EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
    Settings.embed_model = HuggingFaceEmbedding(model_name=hf_embedding_model)

# LLM
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()
if LLM_BACKEND == "openai":
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    Settings.llm = OpenAI(
        api_key=openai_api_key,
        model=openai_model,
        request_timeout=60
    )
else:
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct-q2_K")
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    Settings.llm = Ollama(
        model=ollama_model,
        base_url=ollama_url,
        request_timeout=300
    )

from llama_index.core import StorageContext, load_index_from_storage
persist_dir = "storage"
storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
index = load_index_from_storage(storage_context)
