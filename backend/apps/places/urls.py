from django.urls import path
from .views import (
    ReviewCreateView,
    PlaceSearchView,
    PlaceDetailView,
    PlaceCategoryListView,
    TrendingPlacesView,
    BookmarkToggleView,
    UserBookmarksView,
    ReviewVoteView,
    PlaceStatsView
)

app_name = 'places'

urlpatterns = [
    # Categories
    path('categories/', PlaceCategoryListView.as_view(), name='categories'),
    
    # Reviews
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:review_id>/vote/', ReviewVoteView.as_view(), name='review-vote'),
    
    # Places
    path('search/', PlaceSearchView.as_view(), name='place-search'),
    path('trending/', TrendingPlacesView.as_view(), name='trending-places'),
    path('<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
    
    # Bookmarks
    path('<int:place_id>/bookmark/', BookmarkToggleView.as_view(), name='bookmark-toggle'),
    path('bookmarks/', UserBookmarksView.as_view(), name='user-bookmarks'),
    
    # Stats
    path('stats/', PlaceStatsView.as_view(), name='stats'),
]