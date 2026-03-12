"""
URL routing for Customer Management API

Provides router configuration for DRF ViewSets
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, ContactViewSet, USDOTProfileViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'usdot-profiles', USDOTProfileViewSet, basename='usdotprofile')

urlpatterns = [
    path('', include(router.urls)),
]
