#this script populates the database with realistic test data for users, places, and reviews.

import random
from faker import Faker
from django.contrib.auth import get_user_model
from apps.places.models import Place, Review
from django.db import IntegrityError

User = get_user_model()
fake = Faker()

def populate_data():
    """
    Generate realistic test data.
    
    What we create:
    - 50 users with realistic names and phone numbers
    - 100 places (restaurants, shops, doctors, etc.)
    - 500 reviews with varied ratings and text
    """
    
    print("Starting data population...")
    
    # Clear existing data (optional - comment out if you want to keep data)
    print("Clearing existing data...")
    Review.objects.all().delete()
    Place.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    
    # Create users
    print("Creating users...")
    users = []
    for i in range(50):
        phone = f"+1{fake.numerify('##########')}"  # US phone format
        user = User.objects.create_user(
            phone_number=phone,
            name=fake.name(),
            password='password123'  # Same password for easy testing
        )
        users.append(user)
        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1} users...")
    
    print(f"✓ Created {len(users)} users")
    
    # Create places
    print("Creating places...")
    place_types = [
        'Restaurant', 'Cafe', 'Shop', 'Doctor', 'Dentist',
        'Gym', 'Salon', 'Bakery', 'Bar', 'Hotel'
    ]
    
    places = []
    for i in range(100):
        place_type = random.choice(place_types)
        name = f"{fake.company()} {place_type}"
        address = fake.address()
        
        try:
            place = Place.objects.create(
                name=name,
                address=address
            )
            places.append(place)
        except IntegrityError:
            continue
        
        if (i + 1) % 20 == 0:
            print(f"  Created {i + 1} places...")
    
    print(f"✓ Created {len(places)} places")
    
    # Create reviews
    print("Creating reviews...")
    review_texts = [
        "Great experience! Highly recommend.",
        "Good service, will come back again.",
        "Average, nothing special.",
        "Not satisfied with the quality.",
        "Excellent! Best in town.",
        "Decent place, reasonable prices.",
        "Very professional and friendly staff.",
        "Could be better, but okay overall.",
        "Outstanding service and quality!",
        "Disappointed, expected more.",
    ]
    
    reviews = []
    for i in range(500):
        place = random.choice(places)
        user = random.choice(users)
        rating = random.choices(
            [1, 2, 3, 4, 5],
            weights=[5, 10, 20, 30, 35]  # More positive reviews
        )[0]
        text = random.choice(review_texts)
        
        review = Review.objects.create(
            place=place,
            user=user,
            rating=rating,
            text=text
        )
        reviews.append(review)
        
        if (i + 1) % 100 == 0:
            print(f"  Created {i + 1} reviews...")
    
    print(f"✓ Created {len(reviews)} reviews")
    
    # Summary statistics
    print("\n" + "="*50)
    print("DATA POPULATION COMPLETE")
    print("="*50)
    print(f"Users: {User.objects.count()}")
    print(f"Places: {Place.objects.count()}")
    print(f"Reviews: {Review.objects.count()}")
    print("\nSample login credentials:")
    print("Phone: +11234567890")
    print("Password: password123")
    print("(All users have the same password for testing)")
    print("="*50)

# Run the population
populate_data()