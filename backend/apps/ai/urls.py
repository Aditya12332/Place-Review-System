from django.urls import path
from .views import (
    PlaceAISummaryView,
    RegenerateSummaryView,
    SearchSuggestionsView,
    PersonalizedRecommendationsView,
    PlaceQuestionAnswerView,
    RAGStatsView
)

app_name = 'ai'

urlpatterns = [
    # Place AI features
    path('places/<int:place_id>/summary/', PlaceAISummaryView.as_view(), name='place-summary'),
    path('places/<int:place_id>/regenerate-summary/', RegenerateSummaryView.as_view(), name='regenerate-summary'),
    path('places/<int:place_id>/ask/', PlaceQuestionAnswerView.as_view(), name='place-qa'),
    
    # Search & recommendations
    path('search-suggestions/', SearchSuggestionsView.as_view(), name='search-suggestions'),
    path('recommendations/', PersonalizedRecommendationsView.as_view(), name='recommendations'),
    
    # System stats
    path('rag-stats/', RAGStatsView.as_view(), name='rag-stats'),
]