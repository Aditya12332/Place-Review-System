from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Place, Review, PlaceCategory, PlacePhoto, ReviewVote, Bookmark
from apps.users.serializers import UserSerializer
from apps.ai.serializers import PlaceAISummarySerializer, ReviewAIAnalysisSerializer


class PlaceCategorySerializer(serializers.ModelSerializer):
    """Serializer for place categories"""
    
    places_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PlaceCategory
        fields = ['id', 'name', 'icon', 'description', 'places_count']
    
    def get_places_count(self, obj):
        return obj.places.count()


class PlacePhotoSerializer(serializers.ModelSerializer):
    """Serializer for place photos"""
    
    uploaded_by = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PlacePhoto
        fields = ['id', 'image_url', 'caption', 'uploaded_by', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ReviewVoteSerializer(serializers.ModelSerializer):
    """Serializer for review votes"""
    
    class Meta:
        model = ReviewVote
        fields = ['id', 'vote_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Enhanced serializer for displaying reviews"""
    
    user = UserSerializer(read_only=True)
    ai_analysis = ReviewAIAnalysisSerializer(read_only=True)
    user_vote = serializers.SerializerMethodField()
    net_votes = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'rating', 'text',
            'helpful_count', 'not_helpful_count', 'net_votes',
            'user_vote', 'ai_analysis',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'helpful_count', 'not_helpful_count']
    
    def get_user_vote(self, obj):
        """Get current user's vote on this review"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            vote = ReviewVote.objects.get(review=obj, user=request.user)
            return vote.vote_type
        except ReviewVote.DoesNotExist:
            return None
    
    def get_net_votes(self, obj):
        """Calculate net helpful votes"""
        return obj.helpful_count - obj.not_helpful_count


class PlaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for place listings"""
    
    category = PlaceCategorySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    primary_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Place
        fields = [
            'id', 'name', 'address', 'category',
            'average_rating', 'total_reviews',
            'is_bookmarked', 'primary_photo', 'view_count'
        ]
    
    def get_average_rating(self, obj):
        if hasattr(obj, 'avg_rating'):
            return round(obj.avg_rating, 2) if obj.avg_rating else 0
        return 0
    
    def get_total_reviews(self, obj):
        if hasattr(obj, 'review_count'):
            return obj.review_count
        return obj.reviews.count()
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Bookmark.objects.filter(user=request.user, place=obj).exists()
    
    def get_primary_photo(self, obj):
        photo = obj.photos.first()
        if photo:
            serializer = PlacePhotoSerializer(photo, context=self.context)
            return serializer.data
        return None


class PlaceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for place details"""
    
    category = PlaceCategorySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    rating_distribution = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    photos = PlacePhotoSerializer(many=True, read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    ai_summary = PlaceAISummarySerializer(read_only=True)
    
    class Meta:
        model = Place
        fields = [
            'id', 'name', 'address', 'category', 'description',
            'average_rating', 'total_reviews', 'rating_distribution',
            'view_count', 'bookmark_count',
            'reviews', 'photos', 'is_bookmarked', 'ai_summary',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'view_count', 'bookmark_count']
    
    def get_average_rating(self, obj):
        if hasattr(obj, 'avg_rating_db'):
            return round(obj.avg_rating_db, 2) if obj.avg_rating_db else 0
        result = obj.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 2) if result['avg'] else 0
    
    def get_total_reviews(self, obj):
        if hasattr(obj, 'review_count_db'):
            return obj.review_count_db
        return obj.reviews.count()
    
    def get_rating_distribution(self, obj):
        """Get count of reviews for each rating (1-5)"""
        distribution = {}
        for rating in range(1, 6):
            count = obj.reviews.filter(rating=rating).count()
            distribution[str(rating)] = count
        return distribution
    
    def get_reviews(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            reviews = obj.reviews.all()[:20]
            return ReviewSerializer(reviews, many=True, context=self.context).data
        
        user = request.user
        
        # User's reviews first, then top helpful, then newest
        user_reviews = obj.reviews.filter(user=user).order_by('-created_at')
        other_reviews = obj.reviews.exclude(user=user).order_by('-helpful_count', '-created_at')[:20]
        
        all_reviews = list(user_reviews) + list(other_reviews)
        
        return ReviewSerializer(all_reviews, many=True, context=self.context).data
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Bookmark.objects.filter(user=request.user, place=obj).exists()


class ReviewCreateSerializer(serializers.Serializer):
    """Serializer for creating reviews"""
    
    place_name = serializers.CharField(max_length=255)
    place_address = serializers.CharField()
    category_id = serializers.IntegerField(required=False, allow_null=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField()
    
    def validate(self, data):
        if not data.get('text', '').strip():
            raise serializers.ValidationError({
                'text': 'Review text cannot be empty'
            })
        
        # Validate category if provided
        category_id = data.get('category_id')
        if category_id:
            if not PlaceCategory.objects.filter(id=category_id).exists():
                raise serializers.ValidationError({
                    'category_id': 'Invalid category'
                })
        
        return data
    
    def create(self, validated_data):
        from apps.ai.services import ai_service
        from apps.ai.rag_service import rag_service
        from apps.ai.models import ReviewAIAnalysis
        
        place_name = validated_data['place_name']
        place_address = validated_data['place_address']
        category_id = validated_data.get('category_id')
        
        # Get or create place
        place_data = {
            'name': place_name,
            'address': place_address
        }
        if category_id:
            place_data['category_id'] = category_id
        
        place, created = Place.objects.get_or_create(
            name=place_name,
            address=place_address,
            defaults=place_data
        )
        
        # Create review
        review = Review.objects.create(
            place=place,
            user=self.context['request'].user,
            rating=validated_data['rating'],
            text=validated_data['text']
        )
        
        # Add to RAG system asynchronously (don't block request)
        try:
            rag_service.add_review(
                review_id=review.id,
                review_text=review.text,
                place_id=place.id,
                rating=review.rating,
                metadata={
                    'user_id': review.user.id,
                    'created_at': review.created_at.isoformat()
                }
            )
            
            # Analyze review sentiment
            analysis_result = ai_service.analyze_review_sentiment(
                review_text=review.text,
                rating=review.rating
            )
            
            # Store analysis
            ReviewAIAnalysis.objects.create(
                review=review,
                sentiment=analysis_result.get('sentiment', 'neutral'),
                sentiment_score=analysis_result.get('sentiment_score', 0),
                quality_score=analysis_result.get('quality_score', 0.5),
                is_spam=analysis_result.get('is_spam', False),
                keywords=analysis_result.get('keywords', []),
                helpful_reason=analysis_result.get('helpful_reason', '')
            )
        except Exception as e:
            # Don't fail review creation if AI processing fails
            import logging
            logging.error(f"Failed to process review with AI: {str(e)}")
        
        return review


class ReviewVoteCreateSerializer(serializers.Serializer):
    """Serializer for voting on reviews"""
    
    vote_type = serializers.ChoiceField(choices=['helpful', 'not_helpful'])
    
    def create(self, validated_data):
        review_id = self.context['review_id']
        user = self.context['request'].user
        vote_type = validated_data['vote_type']
        
        review = Review.objects.get(id=review_id)
        
        # Check if user already voted
        existing_vote = ReviewVote.objects.filter(review=review, user=user).first()
        
        if existing_vote:
            # Update vote counts
            if existing_vote.vote_type == 'helpful':
                review.helpful_count -= 1
            else:
                review.not_helpful_count -= 1
            
            # If same vote, remove it (toggle off)
            if existing_vote.vote_type == vote_type:
                existing_vote.delete()
                review.save()
                return None
            
            # Update to new vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
        else:
            # Create new vote
            existing_vote = ReviewVote.objects.create(
                review=review,
                user=user,
                vote_type=vote_type
            )
        
        # Update review counts
        if vote_type == 'helpful':
            review.helpful_count += 1
        else:
            review.not_helpful_count += 1
        review.save()
        
        return existing_vote


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for bookmarks"""
    
    place = PlaceListSerializer(read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'place', 'created_at']
        read_only_fields = ['id', 'created_at']