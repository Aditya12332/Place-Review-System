from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, Case, When, IntegerField
from .models import Place, Review
from .serializers import (
    PlaceListSerializer,
    PlaceDetailSerializer,
    ReviewCreateSerializer,
    ReviewSerializer
)

# View for creating a review (and place if needed)
class ReviewCreateView(generics.CreateAPIView):
    
    serializer_class = ReviewCreateSerializer
    
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        return Response({
            'review': ReviewSerializer(review).data,
            'message': 'Review created successfully'
        }, status=status.HTTP_201_CREATED)

# View for searching places
class PlaceSearchView(generics.ListAPIView):
    
    serializer_class = PlaceListSerializer
    
    def get_queryset(self):

        queryset = Place.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
        
        # Get query parameters
        name_query = self.request.query_params.get('name', '').strip()
        min_rating = self.request.query_params.get('min_rating', None)
        
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
            # No name search: order by rating
            queryset = queryset.order_by('-avg_rating')
        return queryset

# View for place details
class PlaceDetailView(generics.RetrieveAPIView):

    serializer_class = PlaceDetailSerializer
    queryset = Place.objects.all()

    def get_queryset(self):

        return Place.objects.prefetch_related(
            'reviews__user'  # Prefetch reviews and their users
        ).annotate(
            avg_rating_db=Avg('reviews__rating'),
            review_count_db=Count('reviews')
        )