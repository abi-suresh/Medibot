from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# Folder containing PDFs
DATA_PATH = "data"
DB_FAISS_PATH = "db"

# Load and split PDF documents
def load_documents():
    documents = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_PATH, file))
            documents.extend(loader.load())
    return documents

# Main embedding logic
def main():
    documents = load_documents()
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(documents, embedding_model)
    db.save_local(DB_FAISS_PATH)
    print("✅ Embeddings stored successfully in FAISS DB.")

if __name__ == "__main__":
    main()
