import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from django.conf import settings
import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) Service using ChromaDB
    
    This service:
    1. Stores review embeddings in ChromaDB
    2. Retrieves relevant reviews for AI context
    3. Manages vector database operations
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - only one instance across application"""
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize RAG components"""
        if self._initialized:
            return
        
        try:
            # Create persist directory if not exists
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.Client(Settings(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False
            ))
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="place_reviews",
                metadata={"description": "Embeddings for place reviews"}
            )
            
            logger.info("RAG Service initialized successfully")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {str(e)}")
            raise
    
    def add_review(self, review_id: int, review_text: str, place_id: int, 
                   rating: int, metadata: Dict[str, Any] = None):
        """
        Add a review to the vector database
        
        Args:
            review_id: Unique review ID
            review_text: Review content
            place_id: Associated place ID
            rating: Review rating (1-5)
            metadata: Additional metadata
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(review_text).tolist()
            
            # Prepare metadata
            meta = {
                "place_id": place_id,
                "rating": rating,
                "review_id": review_id,
                **(metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[review_text],
                metadatas=[meta],
                ids=[f"review_{review_id}"]
            )
            
            logger.info(f"Added review {review_id} to vector DB")
            
        except Exception as e:
            logger.error(f"Error adding review to RAG: {str(e)}")
            # Don't raise - non-critical for review creation
    
    def update_review(self, review_id: int, review_text: str, rating: int, 
                     metadata: Dict[str, Any] = None):
        """Update an existing review in the vector database"""
        try:
            embedding = self.embedding_model.encode(review_text).tolist()
            
            meta = metadata or {}
            meta["rating"] = rating
            
            self.collection.update(
                embeddings=[embedding],
                documents=[review_text],
                metadatas=[meta],
                ids=[f"review_{review_id}"]
            )
            
            logger.info(f"Updated review {review_id} in vector DB")
            
        except Exception as e:
            logger.error(f"Error updating review in RAG: {str(e)}")
    
    def delete_review(self, review_id: int):
        """Delete a review from the vector database"""
        try:
            self.collection.delete(ids=[f"review_{review_id}"])
            logger.info(f"Deleted review {review_id} from vector DB")
        except Exception as e:
            logger.error(f"Error deleting review from RAG: {str(e)}")
    
    def search_similar_reviews(self, query: str, place_id: int = None, 
                              top_k: int = None, min_rating: int = None) -> List[Dict]:
        """
        Search for similar reviews using semantic search
        
        Args:
            query: Search query or review text
            place_id: Filter by specific place
            top_k: Number of results to return
            min_rating: Minimum rating filter
        
        Returns:
            List of similar reviews with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare filters
            where_filter = {}
            if place_id:
                where_filter["place_id"] = place_id
            if min_rating:
                where_filter["rating"] = {"$gte": min_rating}
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k or settings.RAG_TOP_K,
                where=where_filter if where_filter else None
            )
            
            # Format results
            similar_reviews = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_reviews.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return similar_reviews
            
        except Exception as e:
            logger.error(f"Error searching similar reviews: {str(e)}")
            return []
    
    def get_place_review_context(self, place_id: int, top_k: int = 10) -> str:
        """
        Get diverse review context for a place (for AI summarization)
        
        Retrieves reviews covering different sentiments and aspects
        """
        try:
            # Get all reviews for the place
            results = self.collection.get(
                where={"place_id": place_id},
                limit=1000  # Max we'll consider
            )
            
            if not results['documents']:
                return ""
            
            # Sort by rating to get diverse perspectives
            reviews_with_ratings = [
                (doc, meta['rating'])
                for doc, meta in zip(results['documents'], results['metadatas'])
            ]
            
            # Get mix of ratings
            reviews_with_ratings.sort(key=lambda x: x[1])
            
            # Select diverse reviews
            total = len(reviews_with_ratings)
            if total <= top_k:
                selected = reviews_with_ratings
            else:
                # Sample from different rating groups
                step = total // top_k
                selected = [reviews_with_ratings[i * step] for i in range(top_k)]
            
            # Format context
            context = "\n\n".join([
                f"[Rating: {rating}/5] {text}"
                for text, rating in selected
            ])
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting place context: {str(e)}")
            return ""
    
    def batch_index_reviews(self, reviews: List[Dict]):
        """
        Batch index multiple reviews (for initial setup or re-indexing)
        
        Args:
            reviews: List of dicts with keys: id, text, place_id, rating
        """
        try:
            if not reviews:
                return
            
            embeddings = []
            documents = []
            metadatas = []
            ids = []
            
            for review in reviews:
                text = review['text']
                embedding = self.embedding_model.encode(text).tolist()
                
                embeddings.append(embedding)
                documents.append(text)
                metadatas.append({
                    'place_id': review['place_id'],
                    'rating': review['rating'],
                    'review_id': review['id']
                })
                ids.append(f"review_{review['id']}")
            
            # Batch add
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Batch indexed {len(reviews)} reviews")
            
        except Exception as e:
            logger.error(f"Error batch indexing reviews: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            count = self.collection.count()
            return {
                'total_reviews': count,
                'embedding_dimension': len(self.embedding_model.encode("test")),
                'model_name': settings.EMBEDDING_MODEL
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}


# Initialize singleton instance
rag_service = RAGService()