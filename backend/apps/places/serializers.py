from rest_framework import serializers
from django.db.models import Avg
from .models import Place, Review
from apps.users.serializers import UserSerializer

# Serializer for displaying reviews.  
class ReviewSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_id', 'rating', 'text',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Ensure rating is between 1-5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

# Serializer for listing places with average rating.
class PlaceListSerializer(serializers.ModelSerializer):
    
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Place
        fields = ['id', 'name', 'average_rating']
# Calculate average rating efficiently.
    def get_average_rating(self, obj):

        if hasattr(obj, 'avg_rating'):
            return round(obj.avg_rating, 2) if obj.avg_rating else 0
        return obj.average_rating
# Detailed serializer for place details page.
class PlaceDetailSerializer(serializers.ModelSerializer):

    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Place
        fields = [
            'id', 'name', 'address', 'average_rating',
            'total_reviews', 'reviews', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_average_rating(self, obj):
        """Calculate average rating."""
        if hasattr(obj, 'avg_rating'):
            return round(obj.avg_rating, 2) if obj.avg_rating else 0
        return obj.average_rating
    
    def get_total_reviews(self, obj):
        """
        Get total review count.
        Prefer annotated value for efficiency.
        """
        if hasattr(obj, 'review_count_db'):
            return obj.review_count_db
        
        return obj.reviews.count()
    
    # Get all reviews with current user's review at top.
    def get_reviews(self, obj):
       
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            reviews = obj.reviews.all()
            return ReviewSerializer(reviews, many=True).data
        
        user = request.user
        
        # Get current user's reviews first, then others
        user_reviews = obj.reviews.filter(user=user).order_by('-created_at')
        other_reviews = obj.reviews.exclude(user=user).order_by('-created_at')
        
        # Combine user reviews first, then others
        all_reviews = list(user_reviews) + list(other_reviews)
        
        return ReviewSerializer(all_reviews, many=True).data

# Serializer for creating reviews and places if needed.
class ReviewCreateSerializer(serializers.Serializer):
    
    place_name = serializers.CharField(max_length=255)
    place_address = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField()
    
    def validate(self, data):
        """Validate all fields."""
        if not data.get('text', '').strip():
            raise serializers.ValidationError({
                'text': 'Review text cannot be empty'
            })
        return data
    
    def create(self, validated_data):

        place_name = validated_data['place_name']
        place_address = validated_data['place_address']
        
        # Get or create place
        place, created = Place.objects.get_or_create(
            name=place_name,
            address=place_address
        )
        
        # Create review
        review = Review.objects.create(
            place=place,
            user=self.context['request'].user,
            rating=validated_data['rating'],
            text=validated_data['text']
        )
        
        return review