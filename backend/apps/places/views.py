from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Avg, Count, Case, When, IntegerField
from django.shortcuts import get_object_or_404

from .models import Place, Review, PlaceCategory, Bookmark, ReviewVote
from .serializers import (
    PlaceListSerializer,
    PlaceDetailSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
    PlaceCategorySerializer,
    ReviewVoteCreateSerializer,
    BookmarkSerializer
)
import logging

logger = logging.getLogger(__name__)


class PlaceCategoryListView(generics.ListAPIView):
    """
    GET /api/places/categories/
    
    List all place categories
    """
    
    queryset = PlaceCategory.objects.all()
    serializer_class = PlaceCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # No pagination for categories


class ReviewCreateView(generics.CreateAPIView):
    """
    POST /api/places/reviews/
    
    Create a new review for a place
    """
    
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        # Invalidate place summary (will be regenerated on next request)
        try:
            if hasattr(review.place, 'ai_summary'):
                review.place.ai_summary.delete()
        except:
            pass
        
        return Response({
            'review': ReviewSerializer(review, context={'request': request}).data,
            'message': 'Review created successfully'
        }, status=status.HTTP_201_CREATED)


class PlaceSearchView(generics.ListAPIView):
    """
    GET /api/places/search/?name=&min_rating=&category=
    
    Search places with multiple filters
    """
    
    serializer_class = PlaceListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Place.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).select_related('category')
        
        # Get query parameters
        name_query = self.request.query_params.get('name', '').strip()
        min_rating = self.request.query_params.get('min_rating', None)
        category_id = self.request.query_params.get('category', None)
        
        # Filter by category
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        
        # Filter by minimum rating
        if min_rating:
            try:
                min_rating = float(min_rating)
                queryset = queryset.filter(avg_rating__gte=min_rating)
            except (ValueError, TypeError):
                pass
        
        # Search by name
        if name_query:
            queryset = queryset.filter(
                Q(name__iexact=name_query) |
                Q(name__icontains=name_query)
            ).annotate(
                name_match_priority=Case(
                    When(name__iexact=name_query, then=1),
                    default=2,
                    output_field=IntegerField()
                )
            ).order_by('name_match_priority', '-avg_rating')
        else:
            queryset = queryset.order_by('-avg_rating')
        
        return queryset


class PlaceDetailView(generics.RetrieveAPIView):
    """
    GET /api/places/{id}/
    
    Get detailed place information
    """
    
    serializer_class = PlaceDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Place.objects.prefetch_related(
            'reviews__user',
            'reviews__ai_analysis',
            'photos__uploaded_by',
            'ai_summary'
        ).select_related('category').annotate(
            avg_rating_db=Avg('reviews__rating'),
            review_count_db=Count('reviews')
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TrendingPlacesView(generics.ListAPIView):
    """
    GET /api/places/trending/
    
    Get trending places based on recent views and reviews
    """
    
    serializer_class = PlaceListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Place.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(
            review_count__gt=0
        ).order_by('-view_count', '-review_count')[:20]


class BookmarkToggleView(APIView):
    """
    POST /api/places/{place_id}/bookmark/
    
    Toggle bookmark for a place
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, place_id):
        place = get_object_or_404(Place, id=place_id)
        user = request.user
        
        bookmark = Bookmark.objects.filter(user=user, place=place).first()
        
        if bookmark:
            # Remove bookmark
            bookmark.delete()
            place.bookmark_count = max(0, place.bookmark_count - 1)
            place.save(update_fields=['bookmark_count'])
            
            return Response({
                'bookmarked': False,
                'message': 'Bookmark removed'
            }, status=status.HTTP_200_OK)
        else:
            # Add bookmark
            Bookmark.objects.create(user=user, place=place)
            place.bookmark_count += 1
            place.save(update_fields=['bookmark_count'])
            
            return Response({
                'bookmarked': True,
                'message': 'Place bookmarked'
            }, status=status.HTTP_201_CREATED)


class UserBookmarksView(generics.ListAPIView):
    """
    GET /api/places/bookmarks/
    
    Get user's bookmarked places
    """
    
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user
        ).select_related('place__category').prefetch_related('place__photos')


class ReviewVoteView(APIView):
    """
    POST /api/places/reviews/{review_id}/vote/
    
    Vote on a review (helpful/not helpful)
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        
        # Can't vote on own review
        if review.user == request.user:
            return Response({
                'error': 'Cannot vote on your own review'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ReviewVoteCreateSerializer(
            data=request.data,
            context={'request': request, 'review_id': review_id}
        )
        serializer.is_valid(raise_exception=True)
        vote = serializer.save()
        
        # Refresh review from DB
        review.refresh_from_db()
        
        return Response({
            'vote_type': vote.vote_type if vote else None,
            'helpful_count': review.helpful_count,
            'not_helpful_count': review.not_helpful_count,
            'message': 'Vote recorded' if vote else 'Vote removed'
        }, status=status.HTTP_200_OK)


class PlaceStatsView(APIView):
    """
    GET /api/places/stats/
    
    Get overall platform statistics
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        total_places = Place.objects.count()
        total_reviews = Review.objects.count()
        total_users = request.user.__class__.objects.filter(is_active=True).count()
        
        # Top rated places
        top_places = Place.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gte=3).order_by('-avg_rating')[:5]
        
        return Response({
            'total_places': total_places,
            'total_reviews': total_reviews,
            'total_users': total_users,
            'top_places': PlaceListSerializer(
                top_places,
                many=True,
                context={'request': request}
            ).data
        }, status=status.HTTP_200_OK)