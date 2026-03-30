
import os
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

os.environ["GOOGLE_API_KEY"] = "AIzaSyC502QEpdbKesz9vgW_nDnIJj97kGAkS0w"
CHROMA_PATH = "./chroma_db"

def finish_ingestion():
    # 1. Re-load the same documents and chunks
    loader = DirectoryLoader("./policy_knowledge_base", glob="*.md", loader_cls=TextLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    
    print(f"Total chunks expected: {len(chunks)}")
    
    # 2. Setup Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="retrieval_document"
    )

    # 3. Connect to EXISTING DB
    vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # 4. Identify the missing pieces
    # We started failing at chunk 210. Let's pick up from 205 just to be safe.
    remaining_chunks = chunks[205:] 
    print(f"Resuming ingestion for remaining {len(remaining_chunks)} chunks...")

    batch_size = 5
    for i in range(0, len(remaining_chunks), batch_size):
        batch = remaining_chunks[i:i + batch_size]
        try:
            vector_db.add_documents(batch)
            print(f"  - Ingested batch {i//batch_size + 1}")
            time.sleep(5) # Slightly longer sleep to avoid triggering the 429 again
        except Exception as e:
            print(f"⚠️ Still hitting limits. Let's wait 60 seconds...")
            time.sleep(60)
            vector_db.add_documents(batch)

    print("✅ Knowledge Base is now 100% indexed.")

if __name__ == "__main__":
    finish_ingestion()