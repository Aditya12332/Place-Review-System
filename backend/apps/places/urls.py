from django.urls import path
from .views import (
    ReviewCreateView,
    PlaceSearchView,
    PlaceDetailView
)

app_name = 'places'

urlpatterns = [
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('search/', PlaceSearchView.as_view(), name='place-search'),
    path('<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
]