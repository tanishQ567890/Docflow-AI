from pathlib import Path
from langchain_community.document_loaders import (PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredPowerPointLoader)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import PROJECT_ROOT, UPLOAD_FOLDER

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".pptx"}

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

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

vector_path = PROJECT_ROOT / "vectordb"

#loading
def load_pdf():
    """Load the most recently uploaded document."""
    upload_dir = Path(UPLOAD_FOLDER)
    uploaded_files = []
    for ext in SUPPORTED_EXTENSIONS:
        uploaded_files.extend(
            path for path in upload_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ext
        )

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
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

    return embeddings

# Retrieval
def retrieve_documents(question: str):
    """Retrieve relevant document chunks for a question."""
    if not vector_path.is_dir():
        raise FileNotFoundError(
            "No document has been indexed yet. Upload a document before asking questions about it."
        )

    embedding = get_embedding()
    db = FAISS.load_local(
        str(vector_path), embedding, allow_dangerous_deserialization=True
    )
    retriever = db.as_retriever(search_kwargs={"k": 4})
    return retriever.invoke(question)


def save_uploaded_pdf(uploaded_file):
    """Save an uploaded file to the uploads folder."""
    filename = Path(uploaded_file.name.replace("\\", "/")).name
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension or '(none)'}")

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_FOLDER / filename
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path


def index_new_pdf(pdf_path):
    """Index a document into the vector database."""
    loader = get_loader(str(pdf_path))
    documents = loader.load()
    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("The uploaded document contains no extractable text.")

    embedding = get_embedding()
    db = FAISS.from_documents(chunks, embedding)
    db.save_local(str(vector_path))
    return len(chunks)
