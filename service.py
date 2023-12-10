from fastapi import FastAPI, Query
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

print("Building FAISS vector store...")
loader = DirectoryLoader('C:\\Users\\Roger\\bird_descriptions', glob="**/*.txt")
docs = loader.load()
print(f"Loaded {len(docs)} bird descriptions, building embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.from_documents(docs, embeddings)
print(f"Finished embedding descriptions, starting application...")

app = FastAPI()


@app.post("/get_closest_matches")
async def get_closest_matches_endpoint(user_description: str, n: int = Query(1)):
    matching_docs = vectorstore.similarity_search(user_description)
    return {f"guessed_bird_{i}": matching_docs[i].page_content[:100] for i in range(n)}
