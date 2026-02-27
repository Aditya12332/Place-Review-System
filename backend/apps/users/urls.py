from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserStatsView,
    PasswordChangeView,
    UserListView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # User list (for public profiles, leaderboards)
    path('', UserListView.as_view(), name='user-list'),
]