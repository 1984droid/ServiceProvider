"""
Authentication views.

Handles:
- JWT token generation (login)
- Token refresh
- Logout (token blacklist)
- User profile retrieval
- Password management
- User registration (admin only)
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import User

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    UserSerializer,
)


class LoginView(TokenObtainPairView):
    """
    User login endpoint.

    POST /api/auth/login/
    {
        "username": "john.doe",
        "password": "password123"
    }

    Returns:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 1,
            "username": "john.doe",
            "email": "john@example.com",
            ...
            "roles": ["INSPECTOR"],
            "permissions": ["inspections.view_inspectionrun", ...]
        }
    }
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    User logout endpoint.

    POST /api/auth/logout/
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Blacklists the refresh token to prevent further use.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist refresh token."""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred during logout.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(TokenRefreshView):
    """
    Token refresh endpoint.

    POST /api/auth/refresh/
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Returns new access and refresh tokens (if ROTATE_REFRESH_TOKENS=True).
    """
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    Get current user profile.

    GET /api/auth/me/

    Returns complete user profile with permissions and roles.
    Used by frontend on app initialization to restore auth state.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return current user profile."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Update current user profile (limited fields)."""
        # Only allow updating specific fields
        allowed_fields = ['first_name', 'last_name', 'email']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = UserProfileSerializer(
            request.user,
            data=update_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint (Admin only).

    POST /api/auth/register/
    {
        "username": "jane.smith",
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "employee_id": "uuid-here",
        "roles": ["INSPECTOR"]
    }

    Creates new user and optionally links to employee record.
    Only accessible by admin users.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Create user and return profile."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return full user profile
        profile_serializer = UserProfileSerializer(user)
        return Response(
            profile_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ChangePasswordView(APIView):
    """
    Change password endpoint.

    POST /api/auth/change-password/
    {
        "current_password": "OldPass123!",
        "new_password": "NewPass456!",
        "new_password_confirm": "NewPass456!"
    }

    Requires authentication and current password verification.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Change password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """
    List all users (Admin only).

    GET /api/auth/users/

    Returns paginated list of all users with basic info.
    """
    queryset = User.objects.select_related('employee', 'employee__base_department').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    User detail endpoint (Admin only).

    GET /api/auth/users/{id}/
    PATCH /api/auth/users/{id}/
    DELETE /api/auth/users/{id}/

    Full CRUD operations on user accounts.
    """
    queryset = User.objects.select_related('employee', 'employee__base_department').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
