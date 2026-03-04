"""
Test RAG/ChromaDB performance.

Usage:
    python manage.py shell < scripts/test_rag_performance.py
"""

import time
import statistics
from apps.ai.rag_service import rag_service


def test_rag_performance():
    """Test RAG search performance"""
    
    print("\n" + "="*60)
    print("RAG PERFORMANCE TEST")
    print("="*60 + "\n")
    
    # Get stats
    stats = rag_service.get_collection_stats()
    print(f"📊 Vector Database Stats:")
    print(f"  Total embeddings: {stats.get('total_reviews', 0):,}")
    print(f"  Embedding dimension: {stats.get('embedding_dimension', 0)}")
    print(f"  Model: {stats.get('model_name', 'N/A')}\n")
    
    # Test queries
    queries = [
        "great food and service",
        "family friendly restaurant",
        "romantic atmosphere",
        "quick service",
        "affordable prices",
    ]
    
    print("📊 Testing Vector Search Performance...")
    for query in queries:
        times = []
        for i in range(10):
            start = time.time()
            rag_service.search_similar_reviews(query, top_k=10)
            times.append((time.time() - start) * 1000)
        
        print(f"\nQuery: '{query}'")
        print(f"  Average: {statistics.mean(times):.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
    
    print("\n" + "="*60)
    print("✓ RAG TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_rag_performance()