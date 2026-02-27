from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from .models import UserProfile

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    POST /api/users/register/
    
    Register a new user with phone number and name.
    
    Why CreateAPIView?
    - Built-in POST handling
    - Automatic serializer validation
    - Clean, DRY code
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Override to return JWT tokens immediately after registration.
        
        Why? Better UX - user is logged in right after registration.
        Mobile apps can store token and start using the app.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    POST /api/users/login/
    
    Login with phone number and password, returns JWT tokens.
    
    Why GenericAPIView?
    - Need custom post() method
    - Don't need full CRUD operations
    """
    
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        Authenticate user and return JWT tokens.
        
        Why JWT?
        - Stateless: Server doesn't need to store sessions
        - Scalable: No session database lookups
        - Mobile-friendly: Easy to store and send with requests
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last_login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/profile/
    PUT /api/users/profile/
    
    Get or update current authenticated user's profile.
    
    Why RetrieveUpdateAPIView?
    - Handles both GET and PUT/PATCH
    - User can view and edit their own profile
    """
    
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user
    
    def get_serializer_class(self):
        """Use different serializer for updates"""
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer


class UserStatsView(APIView):
    """
    GET /api/users/stats/
    
    Get detailed statistics for current user.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get review statistics
        review_stats = user.reviews.aggregate(
            total_reviews=Count('id'),
            avg_rating=Avg('rating'),
            total_helpful_votes=Count('votes', filter=models.Q(votes__vote_type='helpful'))
        )
        
        # Get places visited
        places_visited = user.reviews.values('place').distinct().count()
        
        # Get bookmarks count
        bookmarks_count = user.bookmarks.count()
        
        # Get recent activity
        recent_reviews = user.reviews.order_by('-created_at')[:5]
        
        return Response({
            'user_id': user.id,
            'name': user.name,
            'member_since': user.date_joined,
            'stats': {
                'total_reviews': review_stats['total_reviews'],
                'average_rating_given': round(review_stats['avg_rating'], 2) if review_stats['avg_rating'] else 0,
                'places_visited': places_visited,
                'bookmarks': bookmarks_count,
                'helpful_votes_received': review_stats['total_helpful_votes'],
            },
            'profile': user.profile.__dict__ if hasattr(user, 'profile') else None
        }, status=status.HTTP_200_OK)


class PasswordChangeView(generics.GenericAPIView):
    """
    POST /api/users/change-password/
    
    Change user password.
    """
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    GET /api/users/
    
    List users (for admin or public profiles).
    Can be used for leaderboards, etc.
    """
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return users with review counts"""
        return User.objects.annotate(
            total_reviews=Count('reviews'),
            average_rating_given=Avg('reviews__rating')
        ).filter(is_active=True).order_by('-date_joined')