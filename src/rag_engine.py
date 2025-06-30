from llama_index.core import VectorStoreIndex, Settings

def build_index(documents, embed_model, llm):
    Settings.embed_model = embed_model
    Settings.llm = llm
    return VectorStoreIndex.from_documents(documents)

def answer_query(index, query):
    return index.as_query_engine().query(query)
