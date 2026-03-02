"""
Test API performance with realistic load.

Usage:
    python manage.py shell < scripts/test_performance.py
"""

import time
import statistics
from django.test import Client
from django.contrib.auth import get_user_model
from apps.places.models import Place

User = get_user_model()


def test_api_performance():
    """Test API endpoints performance"""
    
    print("\n" + "="*60)
    print("API PERFORMANCE TEST")
    print("="*60 + "\n")
    
    client = Client()
    
    # Get test user
    user = User.objects.first()
    if not user:
        print("❌ No users found. Run populate_data first.")
        return
    
    # Login
    response = client.post('/api/users/login/', {
        'phone_number': user.phone_number,
        'password': 'password123'
    }, content_type='application/json')
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json()['tokens']['access']
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # Test 1: Search API
    print("📊 Testing Search API...")
    search_times = []
    for i in range(20):
        start = time.time()
        client.get('/api/places/search/?name=restaurant', **headers)
        search_times.append((time.time() - start) * 1000)
    
    print(f"  Average: {statistics.mean(search_times):.2f}ms")
    print(f"  Median: {statistics.median(search_times):.2f}ms")
    print(f"  Min: {min(search_times):.2f}ms")
    print(f"  Max: {max(search_times):.2f}ms")
    print(f"  P95: {sorted(search_times)[int(len(search_times) * 0.95)]:.2f}ms\n")
    
    # Test 2: Place Detail API
    print("📊 Testing Place Detail API...")
    place = Place.objects.first()
    detail_times = []
    for i in range(20):
        start = time.time()
        client.get(f'/api/places/{place.id}/', **headers)
        detail_times.append((time.time() - start) * 1000)
    
    print(f"  Average: {statistics.mean(detail_times):.2f}ms")
    print(f"  Median: {statistics.median(detail_times):.2f}ms")
    print(f"  P95: {sorted(detail_times)[int(len(detail_times) * 0.95)]:.2f}ms\n")
    
    # Test 3: AI Summary (if available)
    print("📊 Testing AI Summary API...")
    try:
        summary_times = []
        for i in range(5):  # Fewer tests due to API cost
            start = time.time()
            client.get(f'/api/ai/places/{place.id}/summary/', **headers)
            summary_times.append((time.time() - start) * 1000)
        
        print(f"  Average: {statistics.mean(summary_times):.2f}ms")
        print(f"  Median: {statistics.median(summary_times):.2f}ms\n")
    except Exception as e:
        print(f"  ⚠️  AI test skipped: {str(e)}\n")
    
    print("="*60)
    print("✓ PERFORMANCE TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_api_performance()