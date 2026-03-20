import os
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

class VectorStoreManager:
    """
    Manages the local FAISS vector store for the multi-agent RAG workflow.
    Uses HuggingFace embeddings for local dense retrieval.
    """
    def __init__(self, index_path: str = "./data/faiss_index"):
        self.index_path = index_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.vector_store: Optional[FAISS] = None
        self._init_store()

    def _init_store(self):
        """Initialize or load the vector store."""
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True  # Required for FAISS >= 1.7.4 local loads
                )
            except Exception as e:
                print(f"Warning: Could not load existing vector store: {e}")
                self.vector_store = None
        
        # If not loaded, we leave it as None until documents are added

    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store and persist it."""
        if not documents:
            return False
            
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)
            
        # Ensure directory exists before saving
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.vector_store.save_local(self.index_path)
        return True

    def retrieve(self, query: str, top_k: int = 4, score_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Retrieve top_k documents for a given query."""
        if self.vector_store is None:
            return []
            
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        # Filter by threshold (FAISS L2 distance: lower is better)
        # Note: Depending on distance metric, we may need to normalize. 
        # Here we just return the raw L2 distance as 'score' and let the agent decide.
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)  # Lower is generally better in FAISS L2
            })
            
        return formatted_results

# Singleton instance for the backend
vector_store_manager = VectorStoreManager()
