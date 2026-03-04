"""
Enhanced data population script with configurable scale.

Usage:
    # Small dataset (quick testing)
    python manage.py shell -c "from scripts.populate_data import populate_data; populate_data(scale='small')"
    
    # Medium dataset (realistic testing)
    python manage.py shell -c "from scripts.populate_data import populate_data; populate_data(scale='medium')"
    
    # Large dataset (stress testing)
    python manage.py shell -c "from scripts.populate_data import populate_data; populate_data(scale='large')"
    
Or:
    python manage.py shell < scripts/populate_data.py
"""

import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker
from django.contrib.auth import get_user_model
from apps.places.models import Place, Review, PlaceCategory, ReviewVote, Bookmark

User = get_user_model()
fake = Faker()

# Data scale configurations
SCALES = {
    'small': {
        'users': 100,
        'categories': 10,
        'places': 200,
        'reviews': 1500,
        'votes': 3000,
        'bookmarks': 500
    },
    'medium': {
        'users': 1000,
        'categories': 15,
        'places': 2000,
        'reviews': 15000,
        'votes': 30000,
        'bookmarks': 5000
    },
    'large': {
        'users': 5000,
        'categories': 20,
        'places': 10000,
        'reviews': 75000,
        'votes': 150000,
        'bookmarks': 25000
    },
    'xlarge': {  # For stress testing
        'users': 10000,
        'categories': 25,
        'places': 20000,
        'reviews': 150000,
        'votes': 300000,
        'bookmarks': 50000
    }
}


def populate_data(scale='medium', clear_existing=False):
    """
    Generate realistic test data.
    
    Args:
        scale: 'small', 'medium', 'large', or 'xlarge'
        clear_existing: Whether to clear existing data
    """
    
    if scale not in SCALES:
        print(f"Invalid scale. Choose from: {', '.join(SCALES.keys())}")
        return
    
    config = SCALES[scale]
    print(f"\n{'='*60}")
    print(f"POPULATING DATABASE - {scale.upper()} SCALE")
    print(f"{'='*60}\n")
    
    # Clear existing data if requested
    if clear_existing:
        print("⚠️  Clearing existing data...")
        ReviewVote.objects.all().delete()
        Bookmark.objects.all().delete()
        Review.objects.all().delete()
        Place.objects.all().delete()
        PlaceCategory.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        print("✓ Existing data cleared\n")
    
    # Create categories
    print(f"Creating {config['categories']} categories...")
    categories = create_categories(config['categories'])
    print(f"✓ Created {len(categories)} categories\n")
    
    # Create users
    print(f"Creating {config['users']} users...")
    users = create_users(config['users'])
    print(f"✓ Created {len(users)} users\n")
    
    # Create places
    print(f"Creating {config['places']} places...")
    places = create_places(config['places'], categories)
    print(f"✓ Created {len(places)} places\n")
    
    # Create reviews
    print(f"Creating {config['reviews']} reviews...")
    reviews = create_reviews(config['reviews'], users, places)
    print(f"✓ Created {len(reviews)} reviews\n")
    
    # Create votes
    print(f"Creating {config['votes']} review votes...")
    votes = create_votes(config['votes'], users, reviews)
    print(f"✓ Created {len(votes)} votes\n")
    
    # Create bookmarks
    print(f"Creating {config['bookmarks']} bookmarks...")
    bookmarks = create_bookmarks(config['bookmarks'], users, places)
    print(f"✓ Created {len(bookmarks)} bookmarks\n")
    
    # Print statistics
    print_statistics()


def create_categories(count):
    """Create place categories with icons"""
    category_data = [
        ('Restaurant', '🍽️', 'Dining establishments'),
        ('Cafe', '☕', 'Coffee shops and cafes'),
        ('Fast Food', '🍔', 'Quick service restaurants'),
        ('Bar', '🍺', 'Bars and pubs'),
        ('Bakery', '🍰', 'Bakeries and pastry shops'),
        ('Pizza', '🍕', 'Pizza restaurants'),
        ('Asian', '🍜', 'Asian cuisine'),
        ('Italian', '🍝', 'Italian restaurants'),
        ('Mexican', '🌮', 'Mexican food'),
        ('Shop', '🛍️', 'Retail stores'),
        ('Grocery', '🛒', 'Grocery stores'),
        ('Pharmacy', '💊', 'Pharmacies'),
        ('Doctor', '🏥', 'Medical clinics'),
        ('Dentist', '🦷', 'Dental clinics'),
        ('Gym', '💪', 'Fitness centers'),
        ('Salon', '💇', 'Hair salons and spas'),
        ('Hotel', '🏨', 'Hotels and lodging'),
        ('Park', '🌳', 'Parks and recreation'),
        ('Museum', '🏛️', 'Museums and galleries'),
        ('Theater', '🎭', 'Theaters and cinemas'),
        ('Bank', '🏦', 'Banks and ATMs'),
        ('School', '🏫', 'Educational institutions'),
        ('Library', '📚', 'Libraries'),
        ('Gas Station', '⛽', 'Gas stations'),
        ('Car Wash', '🚗', 'Car wash services'),
    ]
    
    categories = []
    for i, (name, icon, desc) in enumerate(category_data[:count]):
        category, created = PlaceCategory.objects.get_or_create(
            name=name,
            defaults={'icon': icon, 'description': desc}
        )
        categories.append(category)
        
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{count}")
    
    return categories


def create_users(count):
    """Create users with realistic data"""
    users = []
    countries = ['+1', '+44', '+91', '+61', '+81', '+33', '+49']
    
    for i in range(count):
        country_code = random.choice(countries)
        phone = f"{country_code}{fake.numerify('##########')}"
        
        # Ensure unique phone
        while User.objects.filter(phone_number=phone).exists():
            phone = f"{country_code}{fake.numerify('##########')}"
        
        user = User.objects.create_user(
            phone_number=phone,
            name=fake.name(),
            password='password123'
        )
        
        # Set realistic join dates (last 2 years)
        days_ago = random.randint(1, 730)
        user.date_joined = timezone.now() - timedelta(days=days_ago)
        user.save(update_fields=['date_joined'])
        
        users.append(user)
        
        if (i + 1) % 500 == 0:
            print(f"  Progress: {i + 1}/{count}")
    
    return users


def create_places(count, categories):
    """Create places with realistic names and addresses"""
    places = []
    
    # Place name templates
    prefixes = ['The', 'Ye Olde', 'Golden', 'Silver', 'Blue', 'Red', 'Green', 
                'Royal', 'Grand', 'Little', 'Big', 'Best', 'Top', 'Prime']
    
    restaurant_names = ['Bistro', 'Grill', 'Kitchen', 'Diner', 'Cafe', 'House',
                       'Place', 'Spot', 'Corner', 'Table', 'Fork', 'Spoon']
    
    shop_names = ['Market', 'Store', 'Shop', 'Emporium', 'Outlet', 'Boutique',
                  'Mall', 'Center', 'Plaza', 'Gallery']
    
    service_names = ['Clinic', 'Center', 'Studio', 'Spa', 'Salon', 'Gym',
                    'Fitness', 'Wellness', 'Health', 'Care']
    
    for i in range(count):
        category = random.choice(categories)
        
        # Generate name based on category
        if 'Restaurant' in category.name or 'Food' in category.name or 'Cafe' in category.name:
            name = f"{random.choice(prefixes)} {fake.last_name()}'s {random.choice(restaurant_names)}"
        elif 'Shop' in category.name or 'Store' in category.name:
            name = f"{fake.last_name()} {random.choice(shop_names)}"
        else:
            name = f"{fake.last_name()} {random.choice(service_names)}"
        
        # Add category name sometimes
        if random.random() > 0.7:
            name = f"{name} - {category.name}"
        
        address = fake.address()
        
        try:
            place = Place.objects.create(
                name=name,
                address=address,
                category=category,
                description=fake.text(max_nb_chars=200) if random.random() > 0.5 else ''
            )
            
            # Set realistic creation dates
            days_ago = random.randint(1, 730)
            place.created_at = timezone.now() - timedelta(days=days_ago)
            place.save(update_fields=['created_at'])
            
            places.append(place)
        except:
            # Skip duplicates
            pass
        
        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i + 1}/{count}")
    
    return places


def create_reviews(count, users, places):
    """Create reviews with realistic distribution"""
    reviews = []
    
    # Review templates with varying quality
    positive_reviews = [
        "Absolutely amazing! Highly recommend this place.",
        "Great experience! Will definitely come back.",
        "Excellent service and quality. Very satisfied.",
        "Outstanding! Exceeded all expectations.",
        "Perfect! Couldn't ask for more.",
        "Fantastic experience from start to finish.",
        "Love this place! Always consistent quality.",
        "Best in town! Five stars all the way.",
        "Incredible! Worth every penny.",
        "Superb quality and amazing atmosphere.",
    ]
    
    good_reviews = [
        "Pretty good overall. Would come back.",
        "Solid experience. Met expectations.",
        "Good quality for the price.",
        "Nice place, friendly staff.",
        "Decent experience, nothing special but good.",
        "Satisfied with the service and quality.",
        "Good choice, would recommend.",
        "Pleasant experience overall.",
    ]
    
    neutral_reviews = [
        "It's okay. Nothing special.",
        "Average experience. Could be better.",
        "Decent but not impressive.",
        "Middle of the road. Fair quality.",
        "Acceptable but room for improvement.",
        "Not bad, not great either.",
    ]
    
    negative_reviews = [
        "Disappointing. Expected better.",
        "Not satisfied with the quality.",
        "Poor service and overpriced.",
        "Would not recommend. Many issues.",
        "Below average. Not worth it.",
        "Unpleasant experience overall.",
    ]
    
    very_negative_reviews = [
        "Terrible experience. Avoid at all costs.",
        "Awful! Worst service ever.",
        "Complete waste of time and money.",
        "Horrible! Never coming back.",
        "Absolutely terrible. Zero stars if possible.",
    ]
    
    # Rating distribution (realistic - skewed positive)
    rating_weights = [3, 5, 15, 30, 47]  # 1-star to 5-star weights
    
    for i in range(count):
        user = random.choice(users)
        place = random.choice(places)
        
        # Select rating with weighted probability
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        
        # Select review text based on rating
        if rating == 5:
            text = random.choice(positive_reviews)
        elif rating == 4:
            text = random.choice(good_reviews)
        elif rating == 3:
            text = random.choice(neutral_reviews)
        elif rating == 2:
            text = random.choice(negative_reviews)
        else:
            text = random.choice(very_negative_reviews)
        
        # Sometimes add more detail
        if random.random() > 0.7:
            text += " " + fake.sentence(nb_words=10)
        
        review = Review.objects.create(
            place=place,
            user=user,
            rating=rating,
            text=text
        )
        
        # Set realistic review dates (after place creation)
        place_age = (timezone.now() - place.created_at).days
        user_age = (timezone.now() - user.date_joined).days
        
        max_days_ago = min(place_age, user_age, 365)
        if max_days_ago > 0:
            days_ago = random.randint(1, max_days_ago)
            review.created_at = timezone.now() - timedelta(days=days_ago)
            review.save(update_fields=['created_at'])
        
        reviews.append(review)
        
        if (i + 1) % 5000 == 0:
            print(f"  Progress: {i + 1}/{count}")
    
    return reviews


def create_votes(count, users, reviews):
    """Create review votes"""
    votes = []
    created_count = 0
    attempts = 0
    max_attempts = count * 2
    
    while created_count < count and attempts < max_attempts:
        attempts += 1
        
        user = random.choice(users)
        review = random.choice(reviews)
        
        # Don't vote on own reviews
        if review.user == user:
            continue
        
        # Check if already voted
        if ReviewVote.objects.filter(user=user, review=review).exists():
            continue
        
        # 70% helpful, 30% not helpful
        vote_type = 'helpful' if random.random() > 0.3 else 'not_helpful'
        
        vote = ReviewVote.objects.create(
            user=user,
            review=review,
            vote_type=vote_type
        )
        
        # Update review counts
        if vote_type == 'helpful':
            review.helpful_count += 1
        else:
            review.not_helpful_count += 1
        review.save(update_fields=['helpful_count', 'not_helpful_count'])
        
        votes.append(vote)
        created_count += 1
        
        if created_count % 10000 == 0:
            print(f"  Progress: {created_count}/{count}")
    
    return votes


def create_bookmarks(count, users, places):
    """Create bookmarks"""
    bookmarks = []
    created_count = 0
    attempts = 0
    max_attempts = count * 2
    
    while created_count < count and attempts < max_attempts:
        attempts += 1
        
        user = random.choice(users)
        place = random.choice(places)
        
        # Check if already bookmarked
        if Bookmark.objects.filter(user=user, place=place).exists():
            continue
        
        bookmark = Bookmark.objects.create(
            user=user,
            place=place
        )
        
        # Update place bookmark count
        place.bookmark_count += 1
        place.save(update_fields=['bookmark_count'])
        
        bookmarks.append(bookmark)
        created_count += 1
        
        if created_count % 5000 == 0:
            print(f"  Progress: {created_count}/{count}")
    
    return bookmarks


def print_statistics():
    """Print database statistics"""
    from django.db.models import Avg, Count
    
    print(f"\n{'='*60}")
    print("DATABASE STATISTICS")
    print(f"{'='*60}\n")
    
    # User stats
    total_users = User.objects.count()
    print(f"👥 Users: {total_users:,}")
    
    # Place stats
    total_places = Place.objects.count()
    places_with_reviews = Place.objects.annotate(
        review_count=Count('reviews')
    ).filter(review_count__gt=0).count()
    print(f"📍 Places: {total_places:,} ({places_with_reviews:,} with reviews)")
    
    # Category stats
    total_categories = PlaceCategory.objects.count()
    print(f"🏷️  Categories: {total_categories}")
    
    # Review stats
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg']
    print(f"⭐ Reviews: {total_reviews:,} (avg rating: {avg_rating:.2f})")
    
    # Vote stats
    total_votes = ReviewVote.objects.count()
    helpful_votes = ReviewVote.objects.filter(vote_type='helpful').count()
    print(f"👍 Votes: {total_votes:,} ({helpful_votes:,} helpful)")
    
    # Bookmark stats
    total_bookmarks = Bookmark.objects.count()
    print(f"🔖 Bookmarks: {total_bookmarks:,}")
    
    # Performance stats
    print(f"\n{'='*60}")
    print("PERFORMANCE INSIGHTS")
    print(f"{'='*60}\n")
    
    # Reviews per place
    avg_reviews_per_place = total_reviews / total_places if total_places > 0 else 0
    print(f"📊 Avg reviews per place: {avg_reviews_per_place:.1f}")
    
    # Reviews per user
    avg_reviews_per_user = total_reviews / total_users if total_users > 0 else 0
    print(f"📊 Avg reviews per user: {avg_reviews_per_user:.1f}")
    
    # Most reviewed places
    top_places = Place.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:5]
    
    print(f"\n🏆 Top 5 Most Reviewed Places:")
    for i, place in enumerate(top_places, 1):
        print(f"  {i}. {place.name} - {place.review_count} reviews")
    
    # Most active users
    from django.db.models import Count
    top_users = User.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:5]
    
    print(f"\n🏆 Top 5 Most Active Users:")
    for i, user in enumerate(top_users, 1):
        print(f"  {i}. {user.name} - {user.review_count} reviews")
    
    print(f"\n{'='*60}")
    print("✓ DATA POPULATION COMPLETE")
    print(f"{'='*60}\n")
    
    print("Sample login credentials:")
    print("Phone: Any from database")
    print("Password: password123")
    print("\nTo get a phone number:")
    sample_user = User.objects.first()
    if sample_user:
        print(f"Example: {sample_user.phone_number}")
    print(f"\n{'='*60}\n")


# Run if executed directly
if __name__ == '__main__':
    populate_data(scale='medium', clear_existing=False)