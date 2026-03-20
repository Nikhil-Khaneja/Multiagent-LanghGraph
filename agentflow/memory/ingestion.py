import json
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from .vector_store import vector_store_manager

class DocumentIngestionPipeline:
    """
    Handles ingestion, chunking, and embedding of text documents
    into the RAG vector store.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_text(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Takes raw text, chunks it, and returns a list of LangChain Document objects.
        """
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            # Inject chunk index into metadata
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            documents.append(Document(page_content=chunk, metadata=chunk_metadata))
            
        return documents

    def ingest_to_vector_store(self, text: str, source_id: str, author: str = "unknown") -> int:
        """
        End-to-end ingestion: chunks text and stores it in FAISS.
        Returns the number of chunks stored.
        """
        metadata = {
            "source_id": source_id,
            "author": author
        }
        
        docs = self.process_text(text, metadata)
        if docs:
            vector_store_manager.add_documents(docs)
            return len(docs)
        return 0

# Singleton pipeline instance
ingestion_pipeline = DocumentIngestionPipeline()
