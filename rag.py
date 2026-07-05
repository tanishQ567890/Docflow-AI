from pathlib import Path
from langchain_community.document_loaders import (PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredPowerPointLoader)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import GOOGLE_API_KEY, UPLOAD_FOLDER

# Supported file extensions
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".csv", ".pptx"]

def get_loader(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext == ".docx":
        return Docx2txtLoader(file_path)
    elif ext == ".txt":
        return TextLoader(file_path, encoding="utf-8")
    elif ext == ".csv":
        return CSVLoader(file_path, encoding="utf-8")
    elif ext == ".pptx":
        return UnstructuredPowerPointLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

vector_path = "vectordb"

#loading
def load_pdf():
    """Load the most recently uploaded document."""
    upload_dir = Path(UPLOAD_FOLDER)
    uploaded_files = []
    for ext in SUPPORTED_EXTENSIONS:
        uploaded_files.extend(upload_dir.glob(f"*{ext}"))

    uploaded_files = sorted(uploaded_files, key=lambda p: p.stat().st_mtime, reverse=True)

    if not uploaded_files:
        raise FileNotFoundError("No documents found in the uploads folder.")

    loader = get_loader(str(uploaded_files[0]))
    documents = loader.load()
    return documents


# chunking
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap = 80)
    chunks = splitter.split_documents(documents)
    return chunks 


# embedding model
def get_embedding():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return embeddings

# Retrieval
def retrieve_documents(question: str):
    """Retrieve relevant document chunks for a question."""
    embedding = get_embedding()
    db = FAISS.load_local(vector_path, embedding, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 4})
    return retriever.invoke(question)


def save_uploaded_pdf(uploaded_file):
    """Save an uploaded file to the uploads folder."""
    save_path = Path(UPLOAD_FOLDER) / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path


def index_new_pdf(pdf_path):
    """Index a document into the vector database."""
    loader = get_loader(str(pdf_path))
    documents = loader.load()
    chunks = split_documents(documents)
    embedding = get_embedding()
    db = FAISS.from_documents(chunks, embedding)
    db.save_local(vector_path)
    return len(chunks)
