"""
Authentication URL configuration.

Provides endpoints for:
- Login (JWT token generation)
- Logout (token blacklist)
- Token refresh
- Current user profile
- Password management
- User administration
"""
from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    MeView,
    RegisterView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
)

urlpatterns = [
    # Authentication
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),

    # User Administration (Admin only)
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/users/', UserListView.as_view(), name='auth-users-list'),
    path('auth/users/<int:pk>/', UserDetailView.as_view(), name='auth-users-detail'),
]
