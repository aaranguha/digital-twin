import chromadb
from chromadb.config import Settings
import os

# Create or load Chroma database
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "../../chroma_db")

class ChromaStore:
    """Wrapper around Chroma for embedding and retrieving documents."""
    
    def __init__(self):
        """Initialize Chroma client and collection."""
        # Create persistent Chroma client
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        
        # Get or create collection named "profile"
        # Collection = database table for storing embeddings
        self.collection = self.client.get_or_create_collection(
            name="profile",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity for retrieval (focused on meaning of document)
        )
    
    def add_documents(self, documents: list, metadatas: list = None):
        """
        Add documents to Chroma.
        
        Args:
            documents: list of text strings to embed and store
            metadatas: list of dicts with metadata (e.g., source filename)
        
        Example:
            store.add_documents(
                documents=["My resume...", "My bio..."],
                metadatas=[
                    {"source": "resume.md"},
                    {"source": "bio.md"}
                ]
            )
        """
        # Generate IDs for each document (simple incrementing)
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Add to collection
        # Chroma automatically converts text to embeddings using default embedder
        self.collection.add(
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )
    
    def query(self, query_text: str, n_results: int = 3):
        """
        Search for documents similar to the query.
        
        Args:
            query_text: user question or search term
            n_results: how many documents to return
        
        Returns:
            dict with "documents", "metadatas", and "distances"
        
        Example:
            results = store.query("What's your background?")
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                print(f"Found: {doc} (from {metadata['source']})")
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
