"""
Test RAG semantic search
Run: python test_rag_search.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from apps.ai.rag_service import rag_service


print("Testing RAG Search")
print("="*60)

# Test queries
queries = [
    "great food",
    "terrible service",
    "family friendly",
    "expensive prices",
    "zebra spaceship quantum pizza"
]

for query in queries:
    print(f"\nQuery: '{query}'")
    results = rag_service.search_similar_reviews(query, top_k=10)
    print(f"Found: {len(results)} results")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. [{result['metadata']['rating']}/5] {result['text'][:80]}...")

print("\n" + "="*60)