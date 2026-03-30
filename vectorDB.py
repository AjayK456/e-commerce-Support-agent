import os
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma  # Ensure you have 'pip install langchain-chroma'
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Configuration
os.environ["GOOGLE_API_KEY"] = "AIzaSyC502QEpdbKesz9vgW_nDnIJj97kGAkS0w"
DATA_DIR = "./policy_knowledge_base"
CHROMA_PATH = "./chroma_db"

def ingest_data():
    print("Reading documents...")
    if not os.path.exists(DATA_DIR):
        print(f"Error: {DATA_DIR} not found.")
        return

    loader = DirectoryLoader(DATA_DIR, glob="*.md", loader_cls=TextLoader)
    documents = loader.load()

    # 2. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # 3. CRITICAL UPDATE: Using the new stable model ID
    print("Initializing the NEW stable embedding model (models/gemini-embedding-001)...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", # <--- CHANGE THIS
        task_type="retrieval_document"
    )

    # 4. Storage with Batching
    print("Starting vectorization...")
    
    # Initialize Chroma
    vector_db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embeddings
    )

    batch_size = 5 
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            vector_db.add_documents(batch)
            print(f"  - Ingested chunks {i} to {i + len(batch)}")
            time.sleep(2) 
        except Exception as e:
            print(f"❌ Error at chunk {i}: {e}")
            # If it still fails, the API key might not have the model enabled yet
            break

    print(f"✅ Stage 2 Complete! Database saved at {CHROMA_PATH}")

if __name__ == "__main__":
    ingest_data()   