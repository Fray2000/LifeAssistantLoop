import requests
from langchain.vectorstores import Chroma
from .file_utils import read_json, write_json

# Custom embedding class for Ollama
class OllamaEmbeddings:
    def __init__(self, model="nomic-embed-text"):
        self.model = model
        self.api_url = "http://localhost:11434/api/embeddings"

    def embed_documents(self, texts):
        return [self._embed(t) for t in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        payload = {"model": self.model, "prompt": text}
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        return response.json()["embedding"]

def initialize_vector_store():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma(persist_directory="memory/embeddings.db", embedding_function=embeddings)
    return vectordb

def add_to_memory(record: dict, memory_json: str) -> None:
    data = read_json(memory_json)
    if not isinstance(data, list):
        data = []
    data.append(record)
    write_json(memory_json, data)
    vectordb = initialize_vector_store()
    vectordb.add_texts([record["text"]], metadatas=[record])
    vectordb.persist()

def retrieve_from_memory(query: str) -> list:
    vectordb = initialize_vector_store()
    docs = vectordb.similarity_search(query, k=5)
    return [doc.metadata for doc in docs]

# Test rapide (désactivé par défaut)
if __name__ == "__main__":
    add_to_memory({"text": "J'aime le cyclisme"}, "../memory/profile.json")
    print(retrieve_from_memory("cyclisme"))
