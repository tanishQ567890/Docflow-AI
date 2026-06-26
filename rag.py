from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import GOOGLE_API_KEY, DATA_FOLDER, UPLOAD_FOLDER
import shutil
import time

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

data_path = str(Path(DATA_FOLDER) / "OOPS TA lab9.pdf")
vector_path = "vectordb"

# Loading of data source
def load_pdf():
    loader = PyPDFLoader(data_path)
    documents = loader.load()
    return documents


# chunking
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 200)
    chunks = splitter.split_documents(documents)
    return chunks 


# embedding model

def get_embedding():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return embeddings

#Vector Database
def vectorDB():
    documents = load_pdf()
    chunks = split_documents(documents)
    embedding = get_embedding()
    print(f"Total chunks to embed: {len(chunks)}")
    
    batch_size = 20
    db = None
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        # Retry with backoff on rate limit errors
        for attempt in range(5):
            try:
                print(f"Processing batch {batch_num} ({len(batch)} chunks)...")
                if db is None:
                    db = FAISS.from_documents(batch, embedding)
                else:
                    batch_db = FAISS.from_documents(batch, embedding)
                    db.merge_from(batch_db)
                break  # Success, move to next batch
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = 60 * (attempt + 1)
                    print(f"Rate limited. Waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    raise
        
        # Small delay between batches to avoid hitting the limit
        if i + batch_size < len(chunks):
            time.sleep(5)
    
    db.save_local(vector_path)
    print("Vector Database created successfully!")

#Retrival of data

def getRetrival():
    embedding = get_embedding()
    db = FAISS.load_local(vector_path, embedding, allow_dangerous_deserialization=True)
    retriver = db.as_retriever(search_kwargs={"k": 4})
    return retriver

# Retrieve documents for LangGraph
def retrieve_documents(question: str):
    retriever = getRetrival()
    docs = retriever.invoke(question)
    return docs

def save_uploaded_pdf(uploaded_file):

    save_path = Path(UPLOAD_FOLDER) / uploaded_file.name

    with open(save_path, "wb") as f:

        f.write(uploaded_file.getbuffer())

    return save_path

def index_new_pdf(pdf_path):

    loader = PyPDFLoader(str(pdf_path))

    documents = loader.load()

    chunks = split_documents(documents)

    embedding = get_embedding()

    db = FAISS.load_local(

        vector_path,

        embedding,

        allow_dangerous_deserialization=True

    )

    new_db = FAISS.from_documents(

        chunks,

        embedding

    )

    db.merge_from(new_db)

    db.save_local(vector_path)

    return len(chunks)


if __name__ == "__main__":

    import os
    if not os.path.exists(vector_path):
        vectorDB()

    retriever = getRetrival()

    docs = retriever.invoke(

        "What is this document about?"

    )

    for doc in docs:

        print("="*60)

        print(doc.page_content.encode('cp1252', errors='replace').decode('cp1252'))

    



